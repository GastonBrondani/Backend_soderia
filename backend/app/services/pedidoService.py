from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy import select, cast, Date
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from datetime import date, datetime

from app.models.pago import Pago
from app.models.pedido import Pedido
from app.models.clienteCuenta import ClienteCuenta
from app.models.medioPago import MedioPago
from app.models.repartoDia import RepartoDia
from app.models.pedidoProducto import PedidoProducto
from app.models.movimientoStock import MovimientoStock        
from app.models.stock import Stock
from app.models.producto import Producto                           
#from app.models.recorrido import Recorrido Ver despues como implementar


from app.schemas.pedido import PedidoOut, PedidoCreate, PedidoConfirmarIn, PedidoCancelarDeudaIn
from app.schemas.clienteCuenta import ClienteCuentaOut
from app.schemas.enumsStock import TipoMovimiento

from app.services.clienteRepartoDiaService import ClienteRepartoDiaService
from app.services.pagoService import PagoService

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
                select(RepartoDia)
                .where(RepartoDia.id_repartodia == data.id_repartodia)
                .with_for_update()
            ).scalar_one_or_none()
            if rep is None:
                raise HTTPException(status_code=404, detail="Reparto del día no encontrado")

            # (opcional) validar empresa
            if hasattr(rep, "id_empresa") and hasattr(ped, "id_empresa") and rep.id_empresa != ped.id_empresa:
                raise HTTPException(status_code=409, detail="El pedido y el reparto pertenecen a empresas distintas")

            # ✅ NUEVO: crear pago si corresponde (y evitar duplicado)
            abonado = _q2(ped.monto_abonado)
            if abonado > 0:
                ya = db.execute(
                    select(Pago.id_pago).where(Pago.id_pedido == ped.id_pedido)
                ).first()
                if ya:
                    raise HTTPException(status_code=409, detail="Ya existe un pago registrado para este pedido.")

                PagoService.crear(
                    db,
                    id_empresa=ped.id_empresa,
                    id_medio_pago=ped.id_medio_pago,
                    fecha=datetime.now(),
                    monto=abonado,
                    tipo_pago="COBRO_PEDIDO",
                    observacion=ped.observacion,
                    legajo=ped.legajo,
                    id_pedido=ped.id_pedido,
                    id_repartodia=data.id_repartodia,
                )

            # 5) Volcar info del pedido a cliente_reparto_dia
            ClienteRepartoDiaService.upsert_desde_pedido(
                db=db,
                id_repartodia=data.id_repartodia,
                legajo=ped.legajo,
                monto_abonado=ped.monto_abonado,
                observacion=ped.observacion,
                bidones_entregado=None,
            )

            # 6) Enlazar y cerrar
            ped.id_repartodia = data.id_repartodia            

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
    
    @staticmethod
    def crear_pedido(db: Session, pedido_create: PedidoCreate) -> PedidoOut:
        total = _q2(pedido_create.monto_total)
        abonado = _q2(pedido_create.monto_abonado or Decimal("0"))

        items = pedido_create.items or []

        try:
            with db.begin():
                # 1) Validar medio de pago
                mp = db.execute(
                    select(MedioPago).where(MedioPago.id_medio_pago == pedido_create.id_medio_pago)
                ).scalar_one_or_none()
                if mp is None:
                    raise HTTPException(status_code=400, detail="id_medio_pago inexistente.")

                # 2) Bloquear/traer cuenta del cliente
                cuenta = db.execute(
                    select(ClienteCuenta)
                    .where(ClienteCuenta.legajo == pedido_create.legajo)
                    .with_for_update()
                ).scalar_one_or_none()
                if cuenta is None:
                    raise HTTPException(status_code=409, detail="El cliente no tiene cuenta creada.")

                # 3) Ajustar deuda / saldo
                deuda_actual = _q2(cuenta.deuda or Decimal("0"))
                saldo_actual = _q2(cuenta.saldo or Decimal("0"))

                if abonado < Decimal("0"):
                    raise HTTPException(status_code=400, detail="monto_abonado no puede ser negativo.")

                pago_disponible = saldo_actual + abonado
                deuda_total = deuda_actual + total

                if pago_disponible >= deuda_total:
                    deuda_nueva = Decimal("0")
                    saldo_nuevo = pago_disponible - deuda_total
                else:
                    deuda_nueva = deuda_total - pago_disponible
                    saldo_nuevo = Decimal("0")

                cuenta.deuda = _q2(deuda_nueva)
                cuenta.saldo = _q2(saldo_nuevo)

                # 4) Crear pedido (guardamos lo que vino del front)
                nuevo = Pedido(
                    **{
                        **pedido_create.model_dump(
                            exclude_unset=True,
                            exclude={"monto_total", "monto_abonado", "items"},
                        ),
                        "monto_total": total,
                        "monto_abonado": abonado,
                    }
                )
                db.add(nuevo)
                db.flush()  # necesitamos nuevo.id_pedido

                # 5) Items: siempre pedido_producto, stock solo si descuenta_stock = True
                if items:
                    total_items = Decimal("0")

                    for item in items:
                        cantidad = _q2(item.cantidad)
                        precio_unitario = _q2(item.precio_unitario)

                        total_items += cantidad * precio_unitario

                        # 5.1) siempre guardamos detalle en pedido_producto
                        pp = PedidoProducto(
                            id_pedido=nuevo.id_pedido,
                            id_producto=item.id_producto,
                            id_combo=item.id_combo if hasattr(item, "id_combo") else None,
                            cantidad=int(cantidad),
                            precio_unitario=str(precio_unitario),
                        )
                        db.add(pp)

                        # 5.2) traemos el producto para ver si descuenta stock
                        prod = db.get(Producto, item.id_producto)
                        if prod is None:
                            raise HTTPException(
                                status_code=400,
                                detail=f"Producto {item.id_producto} inexistente.",
                            )

                        # Si NO descuenta stock (ej: bidón retornable), no tocamos stock ni movimiento
                        if not prod.descuenta_stock:
                            continue

                        # 5.3) actualizar STOCK (empresa + producto)
                        stock_row = db.execute(
                            select(Stock)
                            .where(
                                Stock.id_empresa == pedido_create.id_empresa,
                                Stock.id_producto == item.id_producto,
                            )
                            .with_for_update()
                        ).scalar_one_or_none()

                        if stock_row is None:
                            raise HTTPException(
                                status_code=409,
                                detail=(
                                    f"No hay stock configurado para el producto "
                                    f"{item.id_producto} en la empresa {pedido_create.id_empresa}."
                                ),
                            )

                        stock_actual = _q2(stock_row.cantidad or Decimal("0"))

                        if stock_actual < cantidad:
                            raise HTTPException(
                                status_code=409,
                                detail=(
                                    f"Stock insuficiente para el producto {item.id_producto}. "
                                    f"Disponible: {stock_actual}, requerido: {cantidad}."
                                ),
                            )

                        stock_row.cantidad = _q2(stock_actual - cantidad)

                        # 5.4) Registrar movimiento_stock (EGRESO)
                        ms = MovimientoStock(
                            id_producto=item.id_producto,
                            id_pedido=nuevo.id_pedido,
                            # id_recorrido lo completás cuando tengas la lógica clara
                            fecha=pedido_create.fecha,
                            tipo_movimiento=TipoMovimiento.egreso,
                            cantidad=cantidad,
                            observacion=f"Venta pedido {nuevo.id_pedido}",
                        )
                        db.add(ms)

                    total_items = _q2(total_items)
                    if total_items != total:
                        raise HTTPException(
                            status_code=400,
                            detail=(
                                f"monto_total ({total}) no coincide con suma de items ({total_items}). "
                                "Revisar cálculo en el front."
                            ),
                        )

                return PedidoOut.model_validate(nuevo)

        except HTTPException:
            raise
        except SQLAlchemyError:
            db.rollback()
            raise HTTPException(status_code=500, detail="Error interno al crear el pedido.")
        

    @staticmethod
    def cancelar_deuda(db: Session, data: PedidoCancelarDeudaIn) -> ClienteCuentaOut:
        monto = _q2(data.monto)
        if monto <= Decimal("0"):
            raise HTTPException(status_code=400, detail="El monto debe ser mayor a 0.")

        try:
            with db.begin():
                # 1) Validar medio de pago (opcional, PagoService también lo valida)
                mp = db.execute(
                    select(MedioPago).where(MedioPago.id_medio_pago == data.id_medio_pago)
                ).scalar_one_or_none()
                if mp is None:
                    raise HTTPException(status_code=400, detail="id_medio_pago inexistente.")

                # 2) Traer y bloquear reparto_dia (para obtener empresa + evitar carreras)
                rep = db.execute(
                    select(RepartoDia)
                    .where(RepartoDia.id_repartodia == data.id_repartodia)
                    .with_for_update()
                ).scalar_one_or_none()
                if rep is None:
                    raise HTTPException(status_code=404, detail="Reparto del día no encontrado")

                # 3) ✅ Crear PAGO (esto debe:
                #    - crear pago
                #    - crear caja_empresa
                #    - actualizar cliente_cuenta (deuda/saldo)
                #    - sumar recaudación del reparto (si lo implementaste en PagoService)
                id_empresa = getattr(rep, "id_empresa", None)
                if id_empresa is None:
                    # Si tu RepartoDia no tiene id_empresa, agregá id_empresa al schema y usá data.id_empresa acá.
                    raise HTTPException(status_code=400, detail="No se pudo resolver id_empresa para el pago.")

                PagoService.crear(
                    db,
                    id_empresa=id_empresa,
                    id_medio_pago=data.id_medio_pago,
                    fecha=datetime.now(),
                    monto=monto,
                    tipo_pago="PAGO_DEUDA",
                    observacion=data.observacion or "Pago de cuenta sin pedido",
                    legajo=data.legajo,
                    id_repartodia=data.id_repartodia,
                )

                # 4) Registrar en cliente_reparto_dia (visita sin pedido, solo pago)
                ClienteRepartoDiaService.upsert_desde_pedido(
                    db=db,
                    id_repartodia=data.id_repartodia,
                    legajo=data.legajo,
                    monto_abonado=monto,
                    observacion=data.observacion or "Pago de cuenta sin pedido",
                    bidones_entregado=None,
                )

                # 5) Devolver la cuenta actualizada (releer)
                cuenta = db.execute(
                    select(ClienteCuenta).where(ClienteCuenta.legajo == data.legajo)
                ).scalars().first()

                if cuenta is None:
                    raise HTTPException(status_code=409, detail="El cliente no tiene cuenta creada.")

                db.flush()
                return ClienteCuentaOut.model_validate(cuenta)

        except HTTPException:
            raise
        except SQLAlchemyError:
            db.rollback()
            raise HTTPException(status_code=500, detail="Error interno al cancelar la deuda.")
        
    