from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class CajaEmpresaTotalOut(BaseModel):
    total: Decimal

    model_config = ConfigDict(from_attributes=True)
