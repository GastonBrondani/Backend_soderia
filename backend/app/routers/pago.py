from http.client import HTTPException
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.pedido import PedidoCancelarDeudaIn
from app.schemas.clienteCuenta import ClienteCuentaOut
from app.services.pedidoService import PedidoService
from app.schemas.pago import PagoCreate, PagoLibreIn, PagoLibreOut, PagoOut
from app.services.pagoService import PagoService
from app.services.comprobantePagoService import ComprobantePagoService as ComprobantePagoServiceExtended


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

@router.post("/{id_pago}/comprobante")
def generar_comprobante_pago(
    id_pago: int,
    db: Session = Depends(get_db),
):
    try:
        doc = ComprobantePagoServiceExtended.generar_y_guardar(db, id_pago=id_pago)
        return {
            "id_documento": doc.id_documento,
            "url": doc.url_archivo,
        }
    except Exception as e:
        print("ERROR GENERANDO COMPROBANTE:", repr(e))
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/libre", response_model=PagoLibreOut)
def crear_pago_libre(
    data: PagoLibreIn,
    db: Session = Depends(get_db),
):
    return PagoService.crear_pago_libre(db, data)