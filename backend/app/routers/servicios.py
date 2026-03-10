from decimal import Decimal
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.clienteServicioService import (
    crear_servicio_alquiler_dispenser,
    listar_pendientes_cliente,
    pagar_periodo_servicio,
    actualizar_monto_servicio,
)
from app.schemas.servicios import ServicioMontoUpdate

router = APIRouter(prefix="/servicios", tags=["Servicios"])


@router.post("/clientes/{legajo}/alquiler-dispenser")
def alta_alquiler_dispenser(
    legajo: int,
    monto_mensual: Decimal,
    usar_saldo: bool = False,
    id_medio_pago: int | None = None,
    id_cuenta: int | None = None,
    observacion: str | None = None,
    db: Session = Depends(get_db),
):
    with db.begin():
        srv, per = crear_servicio_alquiler_dispenser(db, legajo, monto_mensual)

        pago, monto = pagar_periodo_servicio(
            db,
            per.id_periodo,
            legajo,
            id_medio_pago=id_medio_pago,
            observacion=observacion or "Alta alquiler dispenser",
            id_cuenta=id_cuenta,
            usar_saldo=usar_saldo,
        )

    return {
        "ok": True,
        "id_cliente_servicio": srv.id_cliente_servicio,
        "id_periodo": per.id_periodo,
        "estado_periodo": per.estado,
        "periodo": per.periodo.isoformat(),
        "id_pago": pago.id_pago if pago else None,
        "monto": str(monto),
        "medio": "saldo" if usar_saldo else "medio_pago",
    }


@router.get("/clientes/{legajo}/pendientes")
def pendientes(legajo: int, db: Session = Depends(get_db)):
    return listar_pendientes_cliente(db, legajo)


@router.post("/periodos/{id_periodo}/pagar")
def pagar(
    id_periodo: int,
    legajo: int,
    id_medio_pago: int | None = None,
    id_cuenta: int | None = None,
    usar_saldo: bool = False,
    observacion: str | None = None,
    db: Session = Depends(get_db),
):
    with db.begin():
        pago, monto = pagar_periodo_servicio(
            db,
            id_periodo,
            legajo,
            id_medio_pago,
            observacion,
            id_cuenta=id_cuenta,
            usar_saldo=usar_saldo,
        )
    return (
        {"ok": True, "id_pago": pago.id_pago, "monto": str(pago.monto)}
        if pago
        else {"ok": True, "id_pago": None, "monto": str(monto)}
    )


@router.patch("/{id_cliente_servicio}/monto")
def patch_monto_servicio(
    id_cliente_servicio: int,
    payload: ServicioMontoUpdate,
    db: Session = Depends(get_db),
):
    with db.begin():
        srv = actualizar_monto_servicio(
            db,
            id_cliente_servicio=id_cliente_servicio,
            nuevo_monto=payload.monto_mensual,
            aplicar_desde=payload.aplicar_desde,
            actualizar_periodos_no_pagados=payload.actualizar_periodos_no_pagados,
        )

    return {
        "ok": True,
        "id_cliente_servicio": srv.id_cliente_servicio,
        "monto_mensual": str(srv.monto_mensual),
    }
