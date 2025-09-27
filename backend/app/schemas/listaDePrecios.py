from typing import Optional, List,TYPE_CHECKING
from datetime import datetime
from pydantic import BaseModel, field_validator

if TYPE_CHECKING:
    from app.schemas.listaPrecioProducto import LPPBasicOut  # evitar import circular




class ListaDePreciosBase(BaseModel):
    nombre: Optional[str] = None
    estado: Optional[str] = None

    @field_validator("nombre", "estado")
    @classmethod
    def strip_strings(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if isinstance(v, str) else v


class ListaDePreciosCreate(ListaDePreciosBase):
    nombre: str
    estado: Optional[str] = "activo"


class ListaDePreciosUpdate(ListaDePreciosBase):
    pass


class ListaDePreciosOut(ListaDePreciosBase):
    id_lista: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True


# Ref liviano para anidar en otros outputs
class ListaDePreciosRefOut(BaseModel):
    id_lista: int
    nombre: str

    class Config:
        from_attributes = True


# (Opcional) Lista expandida con sus precios
class ListaDePreciosWithPreciosOut(ListaDePreciosOut):
    precios: List["LPPBasicOut"] = []  # ver lista_precio_producto.LPPBasicOut