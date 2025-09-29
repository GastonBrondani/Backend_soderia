from pydantic import BaseModel
from typing import Optional

class DiaSemanaBase(BaseModel):
    nombre_dia: str

class DiaSemanaCreate(DiaSemanaBase):
    id_dia: int

class DiaSemanaUpdate(BaseModel):
    nombre_dia: Optional[str] = None

class DiaSemanaOut(DiaSemanaBase):
    id_dia: int

    class Config:
        from_attributes = True
