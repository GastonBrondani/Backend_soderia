from pydantic import BaseModel
from typing import Optional

class ClienteDiaSemanaBase(BaseModel):
    id_cliente: int
    id_dia: int
    turno_visita: Optional[str] = None

class ClienteDiaSemanaCreate(ClienteDiaSemanaBase):
    pass

class ClienteDiaSemanaUpdate(BaseModel):
    turno_visita: Optional[str] = None

class ClienteDiaSemanaOut(ClienteDiaSemanaBase):
    class Config:
        from_attributes = True
