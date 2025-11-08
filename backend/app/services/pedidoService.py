from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy import select, cast, Date
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from datetime import date

from app.models.pedido import Pedido
from app.models.clienteCuenta import ClienteCuenta
from app.models.medioPago import MedioPago
from app.models.repartoDia import RepartoDia
#from app.models.pedidoProducto import PedidoProducto
#from app.models.listaPrecioProducto import ListaPrecioProducto

from app.schemas.pedido import PedidoOut, PedidoCreate, PedidoConfirmarIn

from app.services.clienteRepartoDiaService import ClienteRepartoDiaService

TWOPLACES = Decimal("0.01")

def _q2(v: Decimal | None) -> Decimal:
    v = Decimal("0") if v is None else Decimal(v)
    return v.quantize(TWOPLACES, rounding=ROUND_HALF_UP)

def _bucket_medio_pago(nombre: str) -> str:
    n = (nombre or "").strip().lower()
    if n in {"efectivo", "cash"}:
        return "efectivo"
    if n in {"transferencia", "virtual", "tarjeta", "debito", "crédito", "credito", "qr", "mp", "mercadopago"}:
        return "virtual"
    raise HTTPException(status_code=400, detail=f"medio_pago no soportado: {nombre!r}")

class PedidoService:

    @staticmethod
    def crear_pedido(db: Session, pedido_create: PedidoCreate) -> PedidoOut:
        total = _q2(pedido_create.monto_total)
        abonado = _q2(pedido_create.monto_abonado or Decimal("0"))
        delta_deuda = (total - abonado).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

        try:
            with db.begin():
                # 1) Validar medio de pago y resolver bucket
                mp = db.execute(
                    select(MedioPago).where(MedioPago.id_medio_pago == pedido_create.id_medio_pago)
                ).scalar_one_or_none()
                if mp is None:
                    raise HTTPException(status_code=400, detail="id_medio_pago inexistente.")
                bucket = _bucket_medio_pago(mp.nombre)   # "efectivo" | "virtual"
                # (no lo guardamos en la tabla; lo usamos luego en confirmar)

                # 2) Bloquear/traer cuenta del cliente
                cuenta = db.execute(
                    select(ClienteCuenta)
                    .where(ClienteCuenta.legajo == pedido_create.legajo)
                    .with_for_update()
                ).scalar_one_or_none()
                if cuenta is None:
                    raise HTTPException(status_code=409, detail="El cliente no tiene cuenta creada.")

                # 3) Ajustar deuda por delta
                cuenta.deuda = _q2(cuenta.deuda) + delta_deuda

                # 4) Crear pedido (queda en borrador con su medio de pago elegido)
                nuevo = Pedido(**{
                                    **pedido_create.model_dump(exclude_unset=True, exclude={"monto_total", "monto_abonado"}),
                                     "monto_total": total,
                                     "monto_abonado": abonado,
                            })
                db.add(nuevo)
                db.flush()

                # (Opcional) Si querés devolver también el bucket resuelto:
                # nuevo._bucket_medio = bucket  # solo en memoria, no persistido

                return PedidoOut.model_validate(nuevo)

        except HTTPException:
            # re-lanzo las 400/409 explícitas
            raise
        except SQLAlchemyError:
            db.rollback()
            raise HTTPException(status_code=500, detail="Error interno al crear el pedido.")


    @staticmethod
    def confirmar_pedido(db: Session, id_pedido: int, data: PedidoConfirmarIn) -> PedidoOut:
        with db.begin():
            # 1) Traer pedido y bloquear (evita doble confirmación)
            ped = db.execute(
                select(Pedido).where(Pedido.id_pedido == id_pedido).with_for_update()
            ).scalar_one_or_none()
            if ped is None:
                raise HTTPException(status_code=404, detail="Pedido no encontrado")

            if ped.estado == "confirmado":
                raise HTTPException(status_code=409, detail="El pedido ya está confirmado")
            if ped.id_medio_pago is None:
                raise HTTPException(status_code=400, detail="El pedido no tiene medio de pago")

            # 2) Traer reparto_dia y bloquear
            rep = db.execute(
                select(RepartoDia).where(RepartoDia.id_repartodia == data.id_repartodia).with_for_update()
            ).scalar_one_or_none()
            if rep is None:
                raise HTTPException(status_code=404, detail="Reparto del día no encontrado")

            # (opcional) validar empresa
            if hasattr(rep, "id_empresa") and hasattr(ped, "id_empresa") and rep.id_empresa != ped.id_empresa:
                raise HTTPException(status_code=409, detail="El pedido y el reparto pertenecen a empresas distintas")

            # 3) Resolver bucket según nombre del medio de pago
            mp = db.execute(
                select(MedioPago).where(MedioPago.id_medio_pago == ped.id_medio_pago)
            ).scalar_one_or_none()
            if mp is None:
                raise HTTPException(status_code=400, detail="id_medio_pago del pedido no existe")
            bucket = _bucket_medio_pago(mp.nombre)

            # 4) Sumar recaudación (solo si abonado > 0)
            abonado = _q2(ped.monto_abonado)
            if abonado > 0:
                rep.total_recaudado = _q2(getattr(rep, "total_recaudado", Decimal("0.00"))) + abonado
                if bucket == "efectivo":
                    rep.total_efectivo = _q2(getattr(rep, "total_efectivo", Decimal("0.00"))) + abonado
                else:
                    rep.total_virtual = _q2(getattr(rep, "total_virtual", Decimal("0.00"))) + abonado

            # 5) Volcar info del pedido a cliente_reparto_dia
            ClienteRepartoDiaService.upsert_desde_pedido(
                db=db,
                id_repartodia=data.id_repartodia,
                legajo=ped.legajo,
                monto_abonado=ped.monto_abonado,
                observacion=ped.observacion,
                # si más adelante calculás bidones desde items, pasalo acá:
                bidones_entregado=None,
            )


            # 6) Enlazar y cerrar
            ped.id_repartodia = data.id_repartodia
            ped.estado = "confirmado"

            db.flush()
            return PedidoOut.model_validate(ped)
        
    @staticmethod
    def Listar_pedidos_por_Fecha(db: Session, fecha: date) -> list[PedidoOut]:
        try:
            pedidos = db.execute(
                select(Pedido).where(cast(Pedido.fecha, Date) == fecha)
            ).scalars().all()
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Error al consultar pedidos.")

        if not pedidos:
            raise HTTPException(status_code=404, detail=f"No hay pedidos para la fecha {fecha.isoformat()}")

        return [PedidoOut.model_validate(p) for p in pedidos]
        
    