from __future__ import annotations
from decimal import Decimal
from typing import List
from pydantic import BaseModel, ConfigDict, Field

class PedidoItemIn(BaseModel):
    id_producto: int
    cantidad: int = Field(gt=0)
    # NOTA: el precio_unitario no viene del front; lo calcula el service.

class PedidoItemsBulkIn(BaseModel):
    items: List[PedidoItemIn]

class PedidoItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_producto: int
    cantidad: int
    precio_unitario: Decimal
