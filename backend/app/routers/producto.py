from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.models.producto import Producto
from app.schemas.producto import (
    ProductoCreate, ProductoUpdate, ProductoOut,  # y si querés: ProductoWithPreciosOut
)

router = APIRouter(prefix="/productos", tags=["Producto"])

def _get_producto_or_404(db: Session, id_producto: int) -> Producto:
    obj = db.get(Producto, id_producto)
    if not obj:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return obj

@router.post("/", response_model=ProductoOut, status_code=status.HTTP_201_CREATED)
def crear_producto(payload: ProductoCreate, db: Session = Depends(get_db)):
    data = payload.model_dump(exclude_unset=True)
    obj = Producto(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/", response_model=list[ProductoOut])
def listar_productos(db: Session = Depends(get_db), limit: int = 50, offset: int = 0):
    rows = db.execute(select(Producto).offset(offset).limit(limit)).scalars().all()
    return rows

@router.get("/{id_producto}", response_model=ProductoOut)
def obtener_producto(id_producto: int, db: Session = Depends(get_db)):
    return _get_producto_or_404(db, id_producto)

@router.put("/{id_producto}", response_model=ProductoOut)
def actualizar_producto(id_producto: int, payload: ProductoUpdate, db: Session = Depends(get_db)):
    obj = _get_producto_or_404(db, id_producto)
    updates = payload.model_dump(exclude_unset=True)
    for k, v in updates.items():
        setattr(obj, k, v)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{id_producto}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(id_producto: int, db: Session = Depends(get_db)):
    obj = _get_producto_or_404(db, id_producto)
    db.delete(obj)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)