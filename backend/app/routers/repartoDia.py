from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.core.database import get_db
from app.schemas.repartoDia import (
    RepartoDiaCreate, RepartoDiaUpdate, RepartoDiaOut, RegistrarCobroIn
)
from app.services.repartoDiaService import RepartoDiaService

router = APIRouter(prefix="/repartos-dia", tags=["Reparto Día"])

@router.post("/", response_model=RepartoDiaOut, status_code=status.HTTP_201_CREATED)
def crear_reparto_dia(payload: RepartoDiaCreate, db: Session = Depends(get_db)):
    return RepartoDiaService.create(
        db,
        id_usuario=payload.id_usuario,
        id_empresa=payload.id_empresa,
        fecha=payload.fecha,
        observacion=payload.observacion,
    )

@router.get("/{id_repartodia}", response_model=RepartoDiaOut)
def obtener_reparto_dia(id_repartodia: int, db: Session = Depends(get_db)):
    return RepartoDiaService.get(db, id_repartodia)

@router.get("/", response_model=List[RepartoDiaOut])
def listar_repartos_dia(
    db: Session = Depends(get_db),
    id_usuario: Optional[int] = Query(default=None),
    id_empresa: Optional[int] = Query(default=None),
    fecha_desde: Optional[date] = Query(default=None),
    fecha_hasta: Optional[date] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    return RepartoDiaService.list(
        db,
        id_usuario=id_usuario,
        id_empresa=id_empresa,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        limit=limit,
        offset=offset,
    )

@router.put("/{id_repartodia}", response_model=RepartoDiaOut)
def actualizar_reparto_dia(
    id_repartodia: int, payload: RepartoDiaUpdate, db: Session = Depends(get_db)
):
    return RepartoDiaService.update(
        db,
        id_repartodia=id_repartodia,
        id_usuario=payload.id_usuario,
        id_empresa=payload.id_empresa,
        fecha=payload.fecha,
        observacion=payload.observacion,
    )

@router.delete("/{id_repartodia}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_reparto_dia(id_repartodia: int, db: Session = Depends(get_db)):
    RepartoDiaService.delete(db, id_repartodia=id_repartodia)

#Desabilitado por ahora
#@router.post("/{id_repartodia}/registrar-cobro", response_model=RepartoDiaOut)
#def registrar_cobro(id_repartodia: int, payload: RegistrarCobroIn, db: Session = Depends(get_db)):
#    return RepartoDiaService.registrar_cobro(
#        db,
#        id_repartodia=id_repartodia,
#        efectivo=payload.efectivo,
#        virtual=payload.virtual,
#    )

# Opcional:
@router.post("/{id_repartodia}/cerrar", response_model=RepartoDiaOut)
def cerrar_reparto(id_repartodia: int, db: Session = Depends(get_db)):
    return RepartoDiaService.cerrar(db, id_repartodia=id_repartodia)
