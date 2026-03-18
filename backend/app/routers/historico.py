from fastapi import APIRouter, Query, status, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import Session
from typing import List   


from app.core.database import get_db

from app.models.cliente import Cliente
from app.models.historico import Historico
from app.schemas.historico import HistoricoOut


router = APIRouter(prefix="/historico", tags=["Historico"])

@router.get("/{legajo}",response_model=HistoricoOut, status_code=status.HTTP_200_OK)
def obtener_historico_cliente(legajo: int,db=Depends(get_db)):
    historico = db.query(Historico).filter(Historico.legajo == legajo).first()
    if not historico:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Historico no encontrado")
    return historico

@router.get(
    "/{legajo}/historicos",
    response_model=List[HistoricoOut],
    status_code=status.HTTP_200_OK,
)
def listar_historico_cliente(
    legajo: int,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    cliente = db.get(Cliente, legajo)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    stmt = (
        select(Historico)
        .where(Historico.legajo == legajo)
        .order_by(Historico.fecha.desc())
        .limit(limit)
        .options(selectinload(Historico.tipo_evento))  # 👈 cambio clave
    )
    rows = db.execute(stmt).scalars().all()
    return [HistoricoOut.model_validate(h) for h in rows]
