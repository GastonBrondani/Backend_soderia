from pydantic import BaseModel,ConfigDict
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
     model_config = ConfigDict(from_attributes=True)
