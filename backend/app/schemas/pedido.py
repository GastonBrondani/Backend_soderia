from typing import Optional
from pydantic import BaseModel, field_validator, ConfigDict,Field
from enum import StrEnum
from datetime import datetime
from decimal import Decimal

class EstadoPedido(StrEnum):
    pendiente = "pendiente" #Pendiente de pago, todavia no se pago
    abonado = "abonado" #Total o parcialmente abonado    
    abonado_parcialmente = "abonado parcialmente" #Abonado parcialmente, queda deuda pendiente    
    cliente_no_compra = "cliente no compra" #El cliente no compro nada, este estado hace referencia a que el pedido no existio, es para guardar el historico.
    pedido_postergado = "pedido postergado" #El cliente pidio postergar el pedido para otro momento/horario
    cliente_pago_de_mas = "cliente pago de más" #El cliente pago de mas queda con saldo a favor en cliente cuenta.

class PedidoBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    legajo: int
    id_medio_pago: int                  # NOT NULL en DB
    id_empresa: int = 1
    fecha: datetime = Field(default_factory=datetime.now)  # tu DB es "without time zone"
    monto_total: Decimal
    monto_abonado: Decimal = Decimal("0.00")
    estado: EstadoPedido = EstadoPedido.pendiente
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
