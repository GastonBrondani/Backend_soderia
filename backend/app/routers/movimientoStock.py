from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.models.movimientoStock import MovimientoStock
from app.schemas.movimientoStock import MovimientoCreate, MovimientoOut, TipoMovimiento
from app.services.stockService import StockService

router = APIRouter(prefix="/movimientos-stock", tags=["Movimiento de Stock"])

@router.post("/", response_model=list[MovimientoOut], status_code=status.HTTP_201_CREATED)
def crear(payload: MovimientoCreate, db: Session = Depends(get_db)):
    """
    Crea movimientos y ajusta stock:
      - ingreso/egreso/ajuste: ajusta en empresa indicada
    Devuelve los últimos movimientos del producto para referencia.
    """
    # delta positivo suma, delta negativo resta
    delta = payload.cantidad if payload.tipo_movimiento in (TipoMovimiento.ingreso, TipoMovimiento.ajuste) else -payload.cantidad

    StockService.ajustar_stock(
        db,
        id_producto=payload.id_producto,
        id_empresa=1,  
        delta=delta,
        tipo=payload.tipo_movimiento,
        fecha=payload.fecha,
        observacion=payload.observacion,
        id_pedido=payload.id_pedido,
        id_recorrido=payload.id_recorrido,
    )

    rows = db.execute(
        select(MovimientoStock)
        .where(MovimientoStock.id_producto == payload.id_producto)
        .order_by(MovimientoStock.id_movimiento.desc())
        .limit(2)
    ).scalars().all()
    return rows
