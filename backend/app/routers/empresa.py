from fastapi import APIRouter,Depends,status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from app.models.empresa import Empresa
from app.schemas.empresa import EmpresaCreate

router = APIRouter(prefix="/empresas", tags=["Empresa"])

@router.post("/",status_code=status.HTTP_201_CREATED)
def CrearEmpresa(data: EmpresaCreate, db:Session=Depends(get_db)):
    empresa=Empresa(**data.model_dump())
    db.add(empresa)
    db.commit()
    db.refresh(empresa)
    return empresa

@router.get("/",status_code=status.HTTP_200_OK)
def ObtenerEmpresas(db:Session=Depends(get_db)):
    empresas = db.query(Empresa).all()
    return empresas