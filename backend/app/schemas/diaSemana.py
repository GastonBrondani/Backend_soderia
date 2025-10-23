from pydantic import BaseModel,ConfigDict
from typing import Optional

class DiaSemanaBase(BaseModel):
    nombre_dia: str

class DiaSemanaCreate(DiaSemanaBase):
    id_dia: int

class DiaSemanaUpdate(BaseModel):
    nombre_dia: Optional[str] = None

class DiaSemanaOut(DiaSemanaBase):
    model_config = ConfigDict(from_attributes=True)
    id_dia: int

    
