from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, update, and_, func
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.models.clienteDiaSemana import ClienteDiaSemana
from app.schemas.agenda import AgendaMoverIn
from app.services.agendaService import insertar_cliente_en_agenda


router = APIRouter(prefix="/agenda", tags=["Agenda"])

@router.post("/mover")
def mover_cliente_agenda(payload: AgendaMoverIn, db: Session = Depends(get_db)):
    insertar_cliente_en_agenda(
        db=db,
        id_cliente=payload.id_cliente,
        id_dia=payload.id_dia,
        turno=payload.turno,
        posicion=payload.posicion,
        despues_de_legajo=payload.despues_de_legajo,
    )
    db.commit()
    return {"ok": True}


