from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from app.core.database import get_db
from app.models.stock import Stock
from app.schemas.stock import StockOut
from app.services.stockService import StockService

router = APIRouter(prefix="/stock", tags=["Stock"])

@router.get("/", response_model=list[StockOut])
def listar(
    db: Session = Depends(get_db),
    id_producto: int | None = Query(None),
    id_empresa: int | None = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    stmt = select(Stock)
    if id_producto is not None:
        stmt = stmt.where(Stock.id_producto == id_producto)
    if id_empresa is not None:
        stmt = stmt.where(Stock.id_empresa == id_empresa)
    rows = db.execute(stmt.order_by(Stock.id_stock).limit(limit).offset(offset)).scalars().all()
    return rows

@router.put("/set", response_model=StockOut, status_code=status.HTTP_200_OK)
def set_por_clave(id_producto: int, id_empresa: int, cantidad: int, db: Session = Depends(get_db)):
    """Setea el stock exacto por (id_producto, id_empresa). Upsert + validación no-negativo."""
    return StockService.set_stock(db, id_producto=id_producto, id_empresa=id_empresa, cantidad=cantidad)

@router.delete("/{id_stock}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(id_stock: int, db: Session = Depends(get_db)):
    entity = db.get(Stock, id_stock)
    if not entity:
        raise HTTPException(status_code=404, detail="Stock no encontrado.")
    db.execute(delete(Stock).where(Stock.id_stock == id_stock))
    db.commit()
