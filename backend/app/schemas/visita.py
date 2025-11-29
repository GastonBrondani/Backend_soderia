from datetime import datetime
from typing import Optional,Literal
from pydantic import BaseModel,ConfigDict



class VisitaBase(BaseModel):
    fecha: Optional[datetime] = None  
    estado: Literal[
        "cliente_compra",
        "cliente_no_compra",
        "postergacion_cliente",
    ]

class VisitaCreate(VisitaBase):
    pass

class VisitaOut(VisitaBase):
    model_config = ConfigDict(from_attributes=True)

    id_visita: int
    legajo: int