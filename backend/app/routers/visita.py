from datetime import datetime

from fastapi import Depends,status,APIRouter
from sqlalchemy.orm import Session
from app.core.database import get_db


from app.models.cliente import Cliente
from app.models.visita import Visita
from app.schemas.visita import VisitaCreate, VisitaOut
from app.api.deps import get_cliente_or_404_dep


router = APIRouter(prefix="/visitas",tags=["Visitas"])

@router.post("/{legajo}",response_model=VisitaOut,status_code=status.HTTP_201_CREATED,)
def crear_visita_cliente(payload: VisitaCreate,cliente: Cliente = Depends(get_cliente_or_404_dep), db: Session = Depends(get_db),):
    
    fecha = payload.fecha or datetime.now()

    visita = Visita(
        legajo=cliente.legajo,
        fecha=fecha,
        estado=payload.estado,
    )

    db.add(visita)
    db.commit()
    db.refresh(visita)

    return visita