from datetime import date
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
def alta_alquiler_dispenser(legajo: int, monto_mensual: Decimal, fecha_inicio: date, db: Session = Depends(get_db)):
    with db.begin():
        srv = crear_servicio_alquiler_dispenser(db, legajo, monto_mensual, fecha_inicio)
    return {"ok": True, "id_cliente_servicio": srv.id_cliente_servicio}

@router.get("/clientes/{legajo}/pendientes")
def pendientes(legajo: int, db: Session = Depends(get_db)):
    return listar_pendientes_cliente(db, legajo)

@router.post("/periodos/{id_periodo}/pagar")
def pagar(id_periodo: int, legajo: int, id_medio_pago: int, observacion: str | None = None, db: Session = Depends(get_db)):
    with db.begin():
        pago = pagar_periodo_servicio(db, id_periodo, legajo, id_medio_pago, observacion)
    return {"ok": True, "id_pago": pago.id_pago, "monto": str(pago.monto)}


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