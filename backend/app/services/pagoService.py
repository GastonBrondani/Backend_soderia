from __future__ import annotations

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import nullcontext

from app.models.pago import Pago
from app.models.medioPago import MedioPago
from app.models.clienteCuenta import ClienteCuenta
from app.models.repartoDia import RepartoDia
from app.models.cajaEmpresa import CajaEmpresa
from app.schemas.pago import PagoLibreIn, PagoLibreOut
from app.services.comprobantePagoService import ComprobantePagoService

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

def _aplicar_pago_a_cuenta(cuenta: ClienteCuenta, monto: Decimal) -> None:
    monto = _q2(monto)
    deuda = _q2(cuenta.deuda or Decimal("0"))
    saldo = _q2(cuenta.saldo or Decimal("0"))

    if monto <= deuda:
        cuenta.deuda = _q2(deuda - monto)
    else:
        sobrante = _q2(monto - deuda)
        cuenta.deuda = _q2(Decimal("0"))
        cuenta.saldo = _q2(saldo + sobrante)

def _sumar_recaudacion_reparto(rep: RepartoDia, bucket: str, monto: Decimal) -> None:
    monto = _q2(monto)
    rep.total_recaudado = _q2(getattr(rep, "total_recaudado", Decimal("0.00"))) + monto
    if bucket == "efectivo":
        rep.total_efectivo = _q2(getattr(rep, "total_efectivo", Decimal("0.00"))) + monto
    else:
        rep.total_virtual = _q2(getattr(rep, "total_virtual", Decimal("0.00"))) + monto


class PagoService:

    @staticmethod
    def crear(
        db: Session,
        *,
        id_empresa: int,
        id_medio_pago: int,
        fecha: datetime,
        monto: Decimal,
        tipo_pago: str,
        observacion: str | None = None,
        legajo: int | None = None,
        id_cuenta: int | None = None,
        id_pedido: int | None = None,
        id_repartodia: int | None = None,
        id_cliente_servicio_periodo: int | None = None,
        id_tipo_mov_ingreso: int = 1,
        id_tipo_mov_egreso: int = 2,
        impactar_cuenta: bool = True,
        impactar_reparto: bool = True,
    ) -> Pago:
        monto = _q2(monto)
        if monto <= 0:
            raise HTTPException(status_code=400, detail="monto debe ser > 0")

        started_tx = not db.in_transaction()
        tx_ctx = db.begin() if started_tx else nullcontext()

        try:
            with tx_ctx:
                mp = db.execute(
                    select(MedioPago).where(MedioPago.id_medio_pago == id_medio_pago)
                ).scalar_one_or_none()
                if mp is None:
                    raise HTTPException(status_code=400, detail="id_medio_pago inexistente.")
                bucket = _bucket_medio_pago(mp.nombre)

                if legajo is None and tipo_pago in {"COBRO_PEDIDO", "PAGO_DEUDA"}:
                    raise HTTPException(status_code=400, detail="Falta legajo para pago de cliente.")

                # --- cuenta (si aplica) ---
                cuenta = None
                if legajo is not None:
                    if id_cuenta is None:
                        ids = db.execute(
                            select(ClienteCuenta.id_cuenta).where(ClienteCuenta.legajo == legajo)
                        ).scalars().all()
                        if not ids:
                            raise HTTPException(status_code=409, detail="El cliente no tiene cuenta creada.")
                        if len(ids) > 1:
                            raise HTTPException(status_code=400, detail="El cliente tiene más de una cuenta. Enviar id_cuenta.")
                        id_cuenta = ids[0]

                    cuenta = db.execute(
                        select(ClienteCuenta)
                        .where(ClienteCuenta.legajo == legajo, ClienteCuenta.id_cuenta == id_cuenta)
                        .with_for_update()
                    ).scalar_one_or_none()
                    if cuenta is None:
                        raise HTTPException(status_code=404, detail="Cuenta no encontrada para ese cliente.")

                # --- reparto (si aplica) ---
                rep = None
                if id_repartodia is not None:
                    rep = db.execute(
                        select(RepartoDia)
                        .where(RepartoDia.id_repartodia == id_repartodia)
                        .with_for_update()
                    ).scalar_one_or_none()
                    if rep is None:
                        raise HTTPException(status_code=404, detail="Reparto del día no encontrado")

                # --- crear pago ---
                pago = Pago(
                    id_empresa=id_empresa,
                    legajo=legajo,
                    id_pedido=id_pedido,
                    id_repartodia=id_repartodia,
                    id_medio_pago=id_medio_pago,
                    fecha=fecha,
                    monto=monto,
                    tipo_pago=tipo_pago,
                    observacion=observacion,
                    id_cuenta=id_cuenta,  # ✅ AGREGAR
                    id_cliente_servicio_periodo=id_cliente_servicio_periodo,
                )
                db.add(pago)
                db.flush()

                # --- caja empresa ---
                es_egreso = tipo_pago in {"EGRESO_EMPRESA"}
                id_tipo_mov = id_tipo_mov_egreso if es_egreso else id_tipo_mov_ingreso
                tipo = "egreso" if es_egreso else "ingreso"

                mov = CajaEmpresa(
                    id_empresa=id_empresa,
                    id_tipo_movimiento=id_tipo_mov,
                    id_medio_pago=id_medio_pago,
                    fecha=fecha,
                    tipo=tipo,
                    monto=monto,
                    observacion=(f"PAGO#{pago.id_pago} {tipo_pago} - {observacion}" if observacion else f"PAGO#{pago.id_pago} {tipo_pago}"),
                )
                db.add(mov)

                # --- impactar cuenta/reparto ---
                if cuenta is not None and impactar_cuenta and tipo_pago in {"COBRO_PEDIDO", "PAGO_DEUDA"}:
                    _aplicar_pago_a_cuenta(cuenta, monto)

                if rep is not None and impactar_reparto and tipo_pago in {"COBRO_PEDIDO", "PAGO_DEUDA"}:
                    _sumar_recaudacion_reparto(rep, bucket, monto)

                return pago

        except SQLAlchemyError as e:
            if started_tx:
                db.rollback()
            raise HTTPException(status_code=500, detail=f"Error interno creando pago: {e}")
    
    @staticmethod
    def crear_pago_libre(
        db: Session,
        data: PagoLibreIn,
    ) -> PagoLibreOut:

        # 1️⃣ Crear el pago
        pago = PagoService.crear(
            db,
            id_empresa=data.id_empresa,
            id_medio_pago=data.id_medio_pago,
            fecha=datetime.utcnow(),
            monto=data.monto,
            tipo_pago="PAGO_DEUDA",
            observacion=data.observacion,
            legajo=data.legajo,
            id_cuenta=data.id_cuenta,
            id_repartodia=data.id_repartodia,
        )

        # 2️⃣ Generar y guardar comprobante
        doc = ComprobantePagoService.generar_y_guardar(
            db,
            id_pago=pago.id_pago,
        )

        # 3️⃣ Respuesta para el front
        return PagoLibreOut(
            id_pago=pago.id_pago,
            comprobante_url=doc.url_archivo,
        )
