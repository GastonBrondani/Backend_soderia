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
from app.models.visita import Visita
# from app.models.recorrido import Recorrido Ver despues como implementar


from app.schemas.pedido import (
    PedidoOut,
    PedidoCreate,
    PedidoConfirmarIn,
    PedidoCancelarDeudaIn,
    EstadoPedido,
)
from app.schemas.clienteCuenta import ClienteCuentaOut
from app.schemas.enumsStock import TipoMovimiento

from app.services.clienteRepartoDiaService import ClienteRepartoDiaService
from app.services.pagoService import PagoService
from app.models.comboProducto import ComboProducto


TWOPLACES = Decimal("0.01")


def _q2(v: Decimal | None) -> Decimal:
    v = Decimal("0") if v is None else Decimal(v)
    return v.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def _bucket_medio_pago(nombre: str) -> str:
    n = (nombre or "").strip().lower()
    if n in {"efectivo", "cash"}:
        return "efectivo"
    if n in {
        "transferencia",
        "virtual",
        "tarjeta",
        "debito",
        "crédito",
        "credito",
        "qr",
        "mp",
        "mercadopago",
    }:
        return "virtual"
    raise HTTPException(status_code=400, detail=f"medio_pago no soportado: {nombre!r}")


# helper: aplicar el CARGO del pedido a la cuenta (sin pago)
def _aplicar_compra_a_cuenta(cuenta: ClienteCuenta, total: Decimal) -> None:
    total = _q2(total)
    if total < 0:
        raise HTTPException(
            status_code=400, detail="monto_total no puede ser negativo."
        )

    deuda = _q2(cuenta.deuda or Decimal("0"))
    saldo = _q2(cuenta.saldo or Decimal("0"))

    # Consumir saldo a favor primero
    if saldo >= total:
        saldo = saldo - total
    else:
        faltante = total - saldo
        saldo = Decimal("0")
        deuda = deuda + faltante

    cuenta.saldo = _q2(saldo)
    cuenta.deuda = _q2(deuda)


class PedidoService:
    @staticmethod
    def confirmar_pedido(
        db: Session, id_pedido: int, data: PedidoConfirmarIn
    ) -> PedidoOut:
        with db.begin():
            now = datetime.now()

            # 1) Traer pedido y bloquear
            ped = db.execute(
                select(Pedido).where(Pedido.id_pedido == id_pedido).with_for_update()
            ).scalar_one_or_none()
            if ped is None:
                raise HTTPException(status_code=404, detail="Pedido no encontrado")

            if ped.id_medio_pago is None:
                raise HTTPException(
                    status_code=400, detail="El pedido no tiene medio de pago"
                )

            total = _q2(ped.monto_total or Decimal("0"))
            abonado = _q2(ped.monto_abonado or Decimal("0"))

            if total <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="El pedido no tiene monto_total válido (> 0).",
                )
            if abonado < 0:
                raise HTTPException(
                    status_code=400, detail="monto_abonado no puede ser negativo."
                )

            # 2) Bloquear cuenta (antes que reparto, para no deadlockear con PagoService)
            id_cuenta = getattr(ped, "id_cuenta", None)

            if id_cuenta is None:
                ids = (
                    db.execute(
                        select(ClienteCuenta.id_cuenta).where(
                            ClienteCuenta.legajo == ped.legajo
                        )
                    )
                    .scalars()
                    .all()
                )
                if not ids:
                    raise HTTPException(
                        status_code=409, detail="El cliente no tiene cuenta creada."
                    )
                if len(ids) > 1:
                    raise HTTPException(
                        status_code=400,
                        detail="Pedido sin id_cuenta y cliente con múltiples cuentas. No se puede confirmar.",
                    )
                id_cuenta = ids[0]
                ped.id_cuenta = id_cuenta  # opcional: “autofix” para que quede guardado

            cuenta = db.execute(
                select(ClienteCuenta)
                .where(
                    ClienteCuenta.legajo == ped.legajo,
                    ClienteCuenta.id_cuenta == id_cuenta,
                )
                .with_for_update()
            ).scalar_one_or_none()
            if cuenta is None:
                raise HTTPException(
                    status_code=404, detail="Cuenta no encontrada para ese cliente."
                )

            saldo_antes = _q2(cuenta.saldo or Decimal("0"))

            # 3) Traer reparto_dia y bloquear
            rep = db.execute(
                select(RepartoDia)
                .where(RepartoDia.id_repartodia == data.id_repartodia)
                .with_for_update()
            ).scalar_one_or_none()
            if rep is None:
                raise HTTPException(
                    status_code=404, detail="Reparto del día no encontrado"
                )

            if (
                hasattr(rep, "id_empresa")
                and hasattr(ped, "id_empresa")
                and rep.id_empresa != ped.id_empresa
            ):
                raise HTTPException(
                    status_code=409,
                    detail="El pedido y el reparto pertenecen a empresas distintas",
                )

            # 4) STOCK + MovimientoStock (solo al confirmar)
            items = (
                db.execute(
                    select(PedidoProducto)
                    .where(PedidoProducto.id_pedido == ped.id_pedido)
                    .order_by(PedidoProducto.id_producto)
                )
                .scalars()
                .all()
            )

            # evitar duplicar movimientos si reintentan
            ya_mov = db.execute(
                select(MovimientoStock).where(
                    MovimientoStock.id_pedido == ped.id_pedido
                )
            ).first()
            if ya_mov:
                raise HTTPException(
                    status_code=409,
                    detail="Ya existen movimientos de stock para este pedido.",
                )

            fecha_mov = getattr(ped, "fecha", None) or now

            for it in items:
                # =====================================================
                # PRODUCTO SIMPLE
                # =====================================================
                if it.id_producto is not None:
                    prod = db.get(Producto, it.id_producto)
                    if prod is None:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Producto {it.id_producto} inexistente.",
                        )

                    if not prod.descuenta_stock:
                        continue

                    cantidad = _q2(Decimal(it.cantidad))

                    stock_row = db.execute(
                        select(Stock)
                        .where(
                            Stock.id_empresa == ped.id_empresa,
                            Stock.id_producto == it.id_producto,
                        )
                        .with_for_update()
                    ).scalar_one_or_none()

                    if stock_row is None:
                        raise HTTPException(
                            status_code=409,
                            detail=f"No hay stock para producto {it.id_producto}.",
                        )

                    if stock_row.cantidad < cantidad:
                        raise HTTPException(
                            status_code=409,
                            detail=f"Stock insuficiente producto {it.id_producto}.",
                        )

                    stock_row.cantidad -= cantidad

                    db.add(
                        MovimientoStock(
                            id_producto=it.id_producto,
                            id_pedido=ped.id_pedido,
                            fecha=fecha_mov,
                            tipo_movimiento=TipoMovimiento.egreso,
                            cantidad=cantidad,
                            observacion=f"Venta pedido {ped.id_pedido} (producto)",
                        )
                    )

                # =====================================================
                # COMBO
                # =====================================================
                elif it.id_combo is not None:
                    combo_items = (
                        db.execute(
                            select(ComboProducto).where(
                                ComboProducto.id_combo == it.id_combo
                            )
                        )
                        .scalars()
                        .all()
                    )

                    if not combo_items:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Combo {it.id_combo} no tiene productos.",
                        )

                    for cp in combo_items:
                        prod = db.get(Producto, cp.id_producto)
                        if prod is None:
                            raise HTTPException(
                                status_code=400,
                                detail=f"Producto {cp.id_producto} del combo inexistente.",
                            )

                        if not prod.descuenta_stock:
                            continue

                        cantidad = _q2(Decimal(cp.cantidad * it.cantidad))

                        stock_row = db.execute(
                            select(Stock)
                            .where(
                                Stock.id_empresa == ped.id_empresa,
                                Stock.id_producto == cp.id_producto,
                            )
                            .with_for_update()
                        ).scalar_one_or_none()

                        if stock_row is None:
                            raise HTTPException(
                                status_code=409,
                                detail=f"No hay stock para producto {cp.id_producto}.",
                            )

                        if stock_row.cantidad < cantidad:
                            raise HTTPException(
                                status_code=409,
                                detail=f"Stock insuficiente producto {cp.id_producto}.",
                            )

                        stock_row.cantidad -= cantidad

                        db.add(
                            MovimientoStock(
                                id_producto=cp.id_producto,
                                id_pedido=ped.id_pedido,
                                fecha=fecha_mov,
                                tipo_movimiento=TipoMovimiento.egreso,
                                cantidad=cantidad,
                                observacion=f"Venta pedido {ped.id_pedido} (combo {it.id_combo})",
                            )
                        )

            # 5) CARGO del pedido a la cuenta (acá recién impacta)
            _aplicar_compra_a_cuenta(cuenta, total)

            # 6) Registrar pago (si corresponde) -> aplica pago a cuenta + caja + reparto
            if abonado > 0:
                ya_pago = db.execute(
                    select(Pago.id_pago).where(Pago.id_pedido == ped.id_pedido)
                ).first()
                if ya_pago:
                    raise HTTPException(
                        status_code=409,
                        detail="Ya existe un pago registrado para este pedido."
                    )

                PagoService.crear(
                    db,
                    id_empresa=ped.id_empresa,
                    id_medio_pago=ped.id_medio_pago,
                    fecha=now,
                    monto=abonado,
                    tipo_pago="COBRO_PEDIDO",
                    observacion=ped.observacion,
                    legajo=ped.legajo,
                    id_cuenta=id_cuenta,
                    id_pedido=ped.id_pedido,
                    id_repartodia=data.id_repartodia,
                    impactar_cuenta=True,
                    impactar_reparto=True,
                )

            # 7) EstadoPedido (SIN usar "confirmado")
            # lógica: con lo disponible (saldo previo + abonado) ¿cubre el total?
            pago_disponible = saldo_antes + abonado

            if pago_disponible <= 0:
                ped.estado = EstadoPedido.pendiente
            elif pago_disponible < total:
                ped.estado = EstadoPedido.abonado_parcialmente
            else:
                # está cubierto; si al final el saldo subió vs saldo_antes => cliente pagó de más
                saldo_despues = _q2(cuenta.saldo or Decimal("0"))
                if saldo_despues > saldo_antes:
                    ped.estado = EstadoPedido.cliente_pago_de_mas
                else:
                    ped.estado = EstadoPedido.abonado

            # 8) cliente_reparto_dia
            ClienteRepartoDiaService.upsert_desde_pedido(
                db=db,
                id_repartodia=data.id_repartodia,
                legajo=ped.legajo,
                monto_abonado=ped.monto_abonado,
                observacion=ped.observacion,
                bidones_entregado=None,
            )

            # 9) visita
            fecha_visita = (
                datetime.combine(rep.fecha, now.time())
                if hasattr(rep, "fecha") and rep.fecha
                else now
            )
            db.add(
                Visita(
                    legajo=ped.legajo,
                    fecha=fecha_visita,
                    estado="cliente_compra",
                )
            )

            # 10) Enlazar reparto y cerrar
            ped.id_repartodia = data.id_repartodia

            db.flush()
            return PedidoOut.model_validate(ped)

    @staticmethod
    def Listar_pedidos_por_Fecha(db: Session, fecha: date) -> list[PedidoOut]:
        try:
            pedidos = (
                db.execute(select(Pedido).where(cast(Pedido.fecha, Date) == fecha))
                .scalars()
                .all()
            )
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Error al consultar pedidos.")

        if not pedidos:
            raise HTTPException(
                status_code=404,
                detail=f"No hay pedidos para la fecha {fecha.isoformat()}",
            )

        return [PedidoOut.model_validate(p) for p in pedidos]

    @staticmethod
    def crear_pedido(db: Session, pedido_create: PedidoCreate) -> PedidoOut:
        total = _q2(pedido_create.monto_total)
        abonado = _q2(pedido_create.monto_abonado or Decimal("0"))
        items = pedido_create.items or []

        try:
            # 1) Validar medio de pago
            mp = db.execute(
                select(MedioPago).where(
                    MedioPago.id_medio_pago == pedido_create.id_medio_pago
                )
            ).scalar_one_or_none()
            if mp is None:
                raise HTTPException(
                    status_code=400, detail="id_medio_pago inexistente."
                )

            # 2) Resolver cuenta
            id_cuenta = getattr(pedido_create, "id_cuenta", None)
            ids = (
                db.execute(
                    select(ClienteCuenta.id_cuenta).where(
                        ClienteCuenta.legajo == pedido_create.legajo
                    )
                )
                .scalars()
                .all()
            )

            if not ids:
                raise HTTPException(
                    status_code=409, detail="El cliente no tiene cuenta creada."
                )

            if id_cuenta is None:
                if len(ids) > 1:
                    raise HTTPException(
                        status_code=400,
                        detail="El cliente tiene más de una cuenta. Enviar id_cuenta.",
                    )
                id_cuenta = ids[0]
            else:
                if id_cuenta not in ids:
                    raise HTTPException(
                        status_code=404,
                        detail="Cuenta no encontrada para ese cliente.",
                    )

            # 3) Estado inicial
            estado_inicial = EstadoPedido.pendiente
            if abonado > 0:
                estado_inicial = (
                    EstadoPedido.abonado
                    if abonado >= total
                    else EstadoPedido.abonado_parcialmente
                )

            # 4) Crear pedido
            nuevo = Pedido(
                **{
                    **pedido_create.model_dump(
                        exclude_unset=True,
                        exclude={
                            "monto_total",
                            "monto_abonado",
                            "items",
                            "id_repartodia",
                        },
                    ),
                    "id_cuenta": id_cuenta,
                    "monto_total": total,
                    "monto_abonado": abonado,
                    "estado": estado_inicial,
                }
            )
            db.add(nuevo)
            db.flush()

            total_calculado = Decimal("0")

            # 5) Items
            for item in items:
                cantidad = Decimal(item.cantidad)
                precio_unitario = _q2(item.precio_unitario)
                total_calculado += cantidad * precio_unitario

                if item.id_producto:
                    prod = db.get(Producto, item.id_producto)
                    if not prod:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Producto {item.id_producto} inexistente.",
                        )
                    db.add(
                        PedidoProducto(
                            id_pedido=nuevo.id_pedido,
                            id_producto=item.id_producto,
                            id_combo=None,
                            cantidad=int(cantidad),
                            precio_unitario=precio_unitario,
                        )
                    )

                elif item.id_combo:
                    db.add(
                        PedidoProducto(
                            id_pedido=nuevo.id_pedido,
                            id_producto=None,
                            id_combo=item.id_combo,
                            cantidad=int(cantidad),
                            precio_unitario=precio_unitario,
                        )
                    )

            total_calculado = _q2(total_calculado)
            if total_calculado != total:
                raise HTTPException(
                    status_code=400,
                    detail=f"monto_total ({total}) no coincide con items+servicios ({total_calculado}).",
                )

            db.commit()
            db.refresh(nuevo)

            return PedidoOut.model_validate(nuevo)

        except HTTPException:
            db.rollback()
            raise
        except SQLAlchemyError as e:
            db.rollback()
            print("ERROR SQL crear_pedido:", repr(e))
            raise HTTPException(
                status_code=500,
                detail=str(e),
            )

    @staticmethod
    def cancelar_deuda(db: Session, data: PedidoCancelarDeudaIn) -> ClienteCuentaOut:
        monto = _q2(data.monto)
        if monto <= Decimal("0"):
            raise HTTPException(status_code=400, detail="El monto debe ser mayor a 0.")

        try:
            with db.begin():
                # 1) Validar medio de pago (opcional, PagoService también lo valida)
                mp = db.execute(
                    select(MedioPago).where(
                        MedioPago.id_medio_pago == data.id_medio_pago
                    )
                ).scalar_one_or_none()
                if mp is None:
                    raise HTTPException(
                        status_code=400, detail="id_medio_pago inexistente."
                    )

                # 2) Traer y bloquear reparto_dia (para obtener empresa + evitar carreras)
                rep = db.execute(
                    select(RepartoDia)
                    .where(RepartoDia.id_repartodia == data.id_repartodia)
                    .with_for_update()
                ).scalar_one_or_none()
                if rep is None:
                    raise HTTPException(
                        status_code=404, detail="Reparto del día no encontrado"
                    )

                # 3) ✅ Crear PAGO (esto debe:
                #    - crear pago
                #    - crear caja_empresa
                #    - actualizar cliente_cuenta (deuda/saldo)
                #    - sumar recaudación del reparto (si lo implementaste en PagoService)
                id_empresa = getattr(rep, "id_empresa", None)
                if id_empresa is None:
                    # Si tu RepartoDia no tiene id_empresa, agregá id_empresa al schema y usá data.id_empresa acá.
                    raise HTTPException(
                        status_code=400,
                        detail="No se pudo resolver id_empresa para el pago.",
                    )

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
                cuenta = (
                    db.execute(
                        select(ClienteCuenta).where(ClienteCuenta.legajo == data.legajo)
                    )
                    .scalars()
                    .first()
                )

                if cuenta is None:
                    raise HTTPException(
                        status_code=409, detail="El cliente no tiene cuenta creada."
                    )

                db.flush()
                return ClienteCuentaOut.model_validate(cuenta)

        except HTTPException:
            raise
        except SQLAlchemyError:
            db.rollback()
            raise HTTPException(
                status_code=500, detail="Error interno al cancelar la deuda."
            )
