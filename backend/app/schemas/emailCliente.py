from typing import Optional
from pydantic import BaseModel,field_validator
from typing_extensions import Literal

EstadoMail = Literal["ACTIVO","INACTIVO"]

class MailClienteBase(BaseModel):
    mail: Optional[str] = None
    estado: Optional[EstadoMail] = "ACTIVO"
    observacion: Optional[str] = None

    #Esto es para que si viene un string vacio o con espacios, lo convierta a None
    @field_validator("observacion")
    @classmethod
    def trim_obs(cls, v):
        if v is None:
            return v
        v = v.strip()
        return v or None

class MailClienteCreate(MailClienteBase):
    pass

class MailClienteUpdate(BaseModel):
    mail: Optional[str] = None
    estado: Optional[EstadoMail] = None
    observacion: Optional[str] = None

    @field_validator("observacion")
    @classmethod
    def trim_obs(cls, v):
        if v is None:
            return v
        v = v.strip()
        return v or None

class MailClienteOut(MailClienteBase):
    id_mail: int
    legajo: int


class Config:
    from_attributes = True