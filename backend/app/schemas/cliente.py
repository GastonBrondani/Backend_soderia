from typing import Optional
from pydantic import BaseModel,ConfigDict,model_validator
from app.schemas.persona import PersonaCreate,PersonaOut,PersonaUpdate

class ClienteBase(BaseModel):    
    observacion: Optional[str] = None

class ClienteCreate(ClienteBase):
    # Pasamos el dni para crearlo
    dni: Optional[int] = None
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
    observacion: Optional[str] = None    
    persona: Optional[PersonaUpdate] = None

class ClienteOut(ClienteBase):
    legajo: int
    dni: int
    persona: Optional[PersonaOut] = None
    model_config = ConfigDict(from_attributes=True)