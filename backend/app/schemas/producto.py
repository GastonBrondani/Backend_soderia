from typing import Optional, List,TYPE_CHECKING
from decimal import Decimal
from pydantic import BaseModel, field_validator

if TYPE_CHECKING:
    from app.schemas.listaPrecioProducto import LPPBasicOut  # evitar import circular

class ProductoBase(BaseModel):
    nombre: Optional[str] = None
    estado: Optional[bool] = True
    litros: Optional[Decimal] = None
    tipo_dispenser: Optional[str] = None
    observacion: Optional[str] = None

    @field_validator("nombre", "estado", "tipo_dispenser", "observacion")
    @classmethod
    def strip_strings(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if isinstance(v, str) else v


class ProductoCreate(ProductoBase):
    nombre: str  # obligatorio

class ProductoUpdate(ProductoBase):
    """PATCH/PUT parcial: sólo actualiza lo enviado."""


class ProductoOut(ProductoBase):
    id_producto: int

    class Config:
        from_attributes = True

# --------- “Ref” liviana para anidar en otros outputs ---------
class ProductoRefOut(BaseModel):
    id_producto: int
    nombre: str

    class Config:
        from_attributes = True

# --------- (Opcional) Producto expandido con precios ---------
# Se define el tipo acá y se referencia por string para evitar import circular.
class ProductoWithPreciosOut(ProductoOut):
    precios: List["LPPBasicOut"] = []  # ver lista_precio_producto.LPPBasicOut