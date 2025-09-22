from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, field_validator

class ClienteCuentaBase(BaseModel):
    saldo: Optional[Decimal] = None
    deuda: Optional[Decimal] = None
    estado: Optional[str] = None
    tipo_de_cuenta: Optional[str] = None
    numero_bidones: Optional[int] = None

    #Usado para eliminar espacios en blanco al inicio y final
    @field_validator("estado")
    @classmethod
    def trim_estado(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if isinstance(v, str) else v

    @field_validator("tipo_de_cuenta")
    @classmethod
    def trim_tipo(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if isinstance(v, str) else v
    
class ClienteCuentaCreate(ClienteCuentaBase):
    saldo: Optional[Decimal] = Decimal("0")
    deuda: Optional[Decimal] = Decimal("0")
    numero_bidones: Optional[int] = 0

class ClienteCuentaUpdate(ClienteCuentaBase):
    """Patch/PUT parcial: sólo actualiza lo que envíes."""

class ClienteCuentaOut(ClienteCuentaBase):
    id_cuenta: int
    legajo: int
    saldo: Optional[Decimal] = Decimal("0")
    deuda: Optional[Decimal] = Decimal("0")
    numero_bidones: Optional[int] = 0

    class Config:
        from_attributes = True