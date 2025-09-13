from typing import Optional
from pydantic import BaseModel,field_validator
from typing_extensions import Literal

estadoTelefono = Literal["ACTIVO","INACTIVO"]

class TelefonoClienteBase(BaseModel):
    nro_telefono: Optional[str] = None
    estado: Optional[estadoTelefono] = "ACTIVO"
    observacion: Optional[str] = None

    #Esto es para que si viene un string vacio o con espacios, lo convierta a None
    @field_validator("observacion")
    @classmethod
    def trim_obs(cls, v):
        if v is None:
            return v
        v = v.strip()
        return v or None
    
class TelefonoClienteCreate(TelefonoClienteBase):
    pass


class TelefonoClienteUpdate(BaseModel):
    nro_telefono: Optional[str] = None
    estado: Optional[estadoTelefono] = None
    observacion: Optional[str] = None

    @field_validator("observacion")
    @classmethod
    def trim_obs(cls, v):
        if v is None:
            return v
        v = v.strip()
        return v or None
    
class TelefonoClienteOut(TelefonoClienteBase):
    id_telefono: int
    legajo: int

class Config:
    from_attributes = True

