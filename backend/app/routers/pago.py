from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.pedido import PedidoCancelarDeudaIn
from app.schemas.clienteCuenta import ClienteCuentaOut
from app.services.pedidoService import PedidoService

router = APIRouter(prefix="/pagos", tags=["Pagos"])


@router.post("/cancelar-deuda", response_model=ClienteCuentaOut)
def cancelar_deuda(
    data: PedidoCancelarDeudaIn,
    db: Session = Depends(get_db),
):
    """
    Permite registrar un pago de cuenta SIN generar un pedido.
    Actualiza deuda/saldo y la recaudación del reparto.
    """
    return PedidoService.cancelar_deuda(db, data)
#Este no lo usamos
"""
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
"""
