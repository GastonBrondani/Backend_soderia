from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.persona import Persona
from app.schemas.persona import PersonaCreate,PersonaOut,PersonaUpdate


router = APIRouter(prefix="/personas", tags=["Personas"])

@router.get("/",response_model=List[PersonaOut])
def ListarPersonas(db:Session=Depends(get_db)):
    return db.query(Persona).all()

@router.get("/{dni}",response_model=PersonaOut)
def BuscarPersona(dni:str,db:Session=Depends(get_db)):
    persona = db.get(Persona,dni)
    if not persona:
        raise HTTPException(status_code=404,detail="Persona no encontrada.")
    return persona

@router.post("/",response_model=PersonaOut,status_code=status.HTTP_201_CREATED)
def CrearPersona(data:PersonaCreate,db:Session=Depends(get_db)):
    if db.get(Persona,data.dni):
        raise HTTPException(status_code=409,detail="Ya existe la persona con ese DNI.")
    persona=Persona(**data.model_dump())
    db.add(persona)
    db.commit()
    db.refresh(persona)
    return persona

@router.put("/{dni}",response_model=PersonaOut)
def ActualizarPersona(dni:str,data:PersonaUpdate,db:Session=Depends(get_db)):
    persona = db.get(Persona,dni)
    if not persona:
        raise HTTPException(status_code=404,detail="Persona no encontrada.")
    for campo,valor in data.model_dump(exclude_unset=True).items():
        setattr(persona,campo,valor)
    db.commit()
    db.refresh(persona)
    return persona

@router.delete("/{dni}",status_code=status.HTTP_204_NO_CONTENT)
def EliminarPersona(dni:str,db:Session=Depends(get_db)):
    persona = db.get(Persona,dni)
    if not persona:
        raise HTTPException(status_code=404,detail="Persona no encontrada.")
    db.delete(persona)
    db.commit()
    return None



                

