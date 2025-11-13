from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel, field_validator, ConfigDict,Field
from enum import StrEnum
from datetime import datetime
from decimal import Decimal
from typing import Optional

class EstadoPedido(StrEnum):
    borrador = "borrador"
    confirmado = "confirmado"
    cancelado = "cancelado"

class PedidoBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    legajo: int
    id_medio_pago: int                  # NOT NULL en DB
    id_empresa: int = 1
    fecha: datetime = Field(default_factory=datetime.now)  # tu DB es "without time zone"
    monto_total: Decimal
    monto_abonado: Decimal = Decimal("0.00")
    estado: EstadoPedido = EstadoPedido.borrador
    observacion: Optional[str] = None
    id_repartodia: Optional[int] = None

    @field_validator("estado", "observacion")
    @classmethod
    def strip_strings(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if isinstance(v, str) else v
    

class PedidoCreate(PedidoBase):
    legajo: int  # obligatorio
    id_medio_pago: int  # obligatorio
    id_empresa: int  # obligatorio
    fecha: datetime  # obligatorio
    monto_total: Decimal  # obligatorio

class PedidoOut(PedidoBase):
    model_config = ConfigDict(from_attributes=True)
    id_pedido: int

class PedidoConfirmarIn(BaseModel):
    id_repartodia: int





#EMMA
class PedidoOutCorto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_pedido: int
    fecha: datetime
    estado: Optional[str] = None
    total: Optional[Decimal] = None
