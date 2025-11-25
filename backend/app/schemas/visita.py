from datetime import datetime
from typing import Optional
from pydantic import BaseModel,ConfigDict



class VisitaBase(BaseModel):
    fecha: Optional[datetime] = None  
    estado: str

class VisitaCreate(VisitaBase):
    pass

class VisitaOut(VisitaBase):
    model_config = ConfigDict(from_attributes=True)

    id_visita: int
    legajo: int