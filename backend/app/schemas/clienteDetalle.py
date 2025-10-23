from typing import Optional, List
from pydantic import BaseModel,ConfigDict,Field

#schemas para mostrar detalles relacionados
from app.schemas.persona import PersonaOut
from app.schemas.direccionCliente import DireccionClienteOut


class ClienteDetalleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    legajo: int
    persona: Optional[PersonaOut] = None
    direcciones: List[DireccionClienteOut] = Field(default_factory=list)