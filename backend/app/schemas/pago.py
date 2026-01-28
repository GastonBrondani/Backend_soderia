from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class PagoCreate(BaseModel):
    id_empresa: int
    id_medio_pago: int
    fecha: datetime
    monto: Decimal = Field(gt=0)

    tipo_pago: str
    observacion: Optional[str] = None

    legajo: Optional[int] = None
    id_pedido: Optional[int] = None
    id_repartodia: Optional[int] = None


class PagoOut(BaseModel):
    id_pago: int
    id_empresa: int
    id_medio_pago: int
    fecha: datetime
    monto: Decimal
    tipo_pago: str
    observacion: Optional[str]

    legajo: Optional[int]
    id_pedido: Optional[int]
    id_repartodia: Optional[int]

    class Config:
        from_attributes = True

class PagoLibreIn(BaseModel):
    legajo: int
    id_cuenta: int
    id_empresa: int
    id_medio_pago: int
    monto: Decimal = Field(gt=0)
    observacion: Optional[str] = None
    id_repartodia: Optional[int] = None


class PagoLibreOut(BaseModel):
    id_pago: int
    comprobante_url: str
