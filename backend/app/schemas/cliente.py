from typing import Optional
from pydantic import BaseModel,ConfigDict,model_validator
from app.schemas.persona import PersonaCreate,PersonaOut,PersonaUpdate

class ClienteBase(BaseModel):
    id_empresa: int
    observacion: Optional[str] = None

class ClienteCreate(ClienteBase):
    # Pasamos el dni para crearlo
    dni: Optional[str] = None
    # o pasamos a la persona completa para crearlo
    persona: Optional[PersonaCreate] = None

    @model_validator(mode="after")
    def _check_persona_or_dni(self):
        if not self.dni and not self.persona:
            raise ValueError("Debes enviar 'dni' de una persona existente o 'persona' completa para crearla.")
        if self.dni and self.persona and self.dni != self.persona.dni:
            raise ValueError("Si envías 'dni' y 'persona', ambos deben coincidir.")
        return self
    
class ClienteUpdate(BaseModel):
    id_empresa: Optional[int] = None
    observacion: Optional[str] = None
    # permitir actualizar nombre/apellido de la persona vinculada
    persona: Optional[PersonaUpdate] = None

class ClienteOut(ClienteBase):
    legajo: int
    dni: str
    persona: Optional[PersonaOut] = None
    model_config = ConfigDict(from_attributes=True)