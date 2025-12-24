from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.pago import PagoCreate, PagoOut
from app.services.pagoService import PagoService

router = APIRouter(prefix="/pagos", tags=["Pagos"])

@router.post("", response_model=PagoOut)
def crear_pago(payload: PagoCreate, db: Session = Depends(get_db)):
    return PagoService.crear(
        db,
        id_empresa=payload.id_empresa,
        id_medio_pago=payload.id_medio_pago,
        fecha=payload.fecha,
        monto=payload.monto,
        tipo_pago=payload.tipo_pago,
        observacion=payload.observacion,
        legajo=payload.legajo,
        id_pedido=payload.id_pedido,
        id_repartodia=payload.id_repartodia,
    )
