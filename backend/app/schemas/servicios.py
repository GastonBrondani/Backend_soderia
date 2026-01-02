from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field
from typing import Optional

class ServicioMontoUpdate(BaseModel):
    monto_mensual: Decimal = Field(..., gt=0)
    aplicar_desde: Optional[date] = None
    actualizar_periodos_no_pagados: bool = True
