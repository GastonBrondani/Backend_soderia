from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from app.api.deps import get_cliente_or_404_dep  
from app.core.database import get_db
from app.models.clienteDiaSemana import ClienteDiaSemana
from app.models.diaSemana import DiaSemana
from app.models.cliente import Cliente

router = APIRouter(prefix="/clientes", tags=["Cliente - días de visita"])

# ---- Schemas específicos del router (payload/response del endpoint) ----
class ClienteDiaVisitaIn(BaseModel):
    id_dia: int
    turno_visita: Optional[str] = None  # "mañana", "tarde", etc.

class ClienteDiasVisitaUpsert(BaseModel):
    dias: List[ClienteDiaVisitaIn]

class ClienteDiaVisitaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_dia: int
    nombre_dia: str
    turno_visita: Optional[str] = None


# ---- Helper de validación ----
def _validar_dias_existen(db: Session, ids: List[int]) -> None:
    if not ids:
        return  # permitir limpiar días (lista vacía)
    existentes = {
        row.id_dia
        for row in db.execute(
            select(DiaSemana.id_dia).where(DiaSemana.id_dia.in_(ids))
        ).all()
    }
    faltantes = set(ids) - existentes
    if faltantes:
        raise HTTPException(
            status_code=400,
            detail=f"Días inexistentes: {sorted(faltantes)}"
        )



@router.get("/{legajo}/dias-visita", response_model=List[ClienteDiaVisitaOut])
def listar_dias_visita_cliente(
    cliente: Cliente = Depends(get_cliente_or_404_dep),
    db: Session = Depends(get_db),
):
    stmt = (
        select(
            ClienteDiaSemana.id_dia,
            DiaSemana.nombre_dia,
            ClienteDiaSemana.turno_visita,
        )
        .select_from(ClienteDiaSemana)
        .join(DiaSemana, DiaSemana.id_dia == ClienteDiaSemana.id_dia)
        .where(ClienteDiaSemana.id_cliente == cliente.legajo)
        .order_by(ClienteDiaSemana.id_dia)
    )
    rows = db.execute(stmt).all()
    return [
        ClienteDiaVisitaOut(
            id_dia=r.id_dia,
            nombre_dia=r.nombre_dia,
            turno_visita=r.turno_visita,
        )
        for r in rows
    ]


@router.put("/{legajo}/dias-visita", response_model=List[ClienteDiaVisitaOut])
def upsert_dias_visita_cliente(
    payload: ClienteDiasVisitaUpsert,
    cliente: Cliente = Depends(get_cliente_or_404_dep),
    db: Session = Depends(get_db),
):
    ids = [d.id_dia for d in payload.dias]
    _validar_dias_existen(db, ids)

    # borrar asociaciones actuales del cliente
    db.execute(
        delete(ClienteDiaSemana).where(ClienteDiaSemana.id_cliente == cliente.legajo)
    )

    # insertar nuevas (si hay)
    if payload.dias:
        db.add_all([
            ClienteDiaSemana(
                id_cliente=cliente.legajo,
                id_dia=item.id_dia,
                turno_visita=item.turno_visita,
            )
            for item in payload.dias
        ])

    db.commit()

    # devolver el estado actual (misma consulta que en GET)
    stmt = (
        select(
            ClienteDiaSemana.id_dia,
            DiaSemana.nombre_dia,
            ClienteDiaSemana.turno_visita,
        )
        .select_from(ClienteDiaSemana)
        .join(DiaSemana, DiaSemana.id_dia == ClienteDiaSemana.id_dia)
        .where(ClienteDiaSemana.id_cliente == cliente.legajo)
        .order_by(ClienteDiaSemana.id_dia)
    )
    rows = db.execute(stmt).all()
    return [
        ClienteDiaVisitaOut(
            id_dia=r.id_dia,
            nombre_dia=r.nombre_dia,
            turno_visita=r.turno_visita,
        )
        for r in rows
    ]


@router.delete("/{legajo}/dias-visita/{id_dia}", status_code=204)
def eliminar_dia_visita_cliente(
    id_dia: int,
    cliente: Cliente = Depends(get_cliente_or_404_dep),
    db: Session = Depends(get_db),
):
    db.execute(
        delete(ClienteDiaSemana).where(
            ClienteDiaSemana.id_cliente == cliente.legajo,
            ClienteDiaSemana.id_dia == id_dia,
        )
    )
    db.commit()
