from fastapi import APIRouter, status,Depends, HTTPException
from app.core.database import get_db



from app.schemas.historico import HistoricoOut
from app.models.historico import Historico

router = APIRouter(prefix="/historico", tags=["Historico"])

@router.get("/{legajo}",response_model=HistoricoOut, status_code=status.HTTP_200_OK)
def obtener_historico_cliente(legajo: int,db=Depends(get_db)):
    historico = db.query(Historico).filter(Historico.legajo == legajo).first()
    if not historico:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Historico no encontrado")
    return historico