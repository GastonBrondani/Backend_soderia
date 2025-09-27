from decimal import Decimal
from pydantic import BaseModel, Field

# Para anidar referencias livianas sin ciclos:
from app.schemas.producto import ProductoRefOut
from app.schemas.listaDePrecios import ListaDePreciosRefOut


# --------- Bases / I-O simples ---------
class LPPBase(BaseModel):
    precio: Decimal = Field(..., ge=0)


class LPPCreate(LPPBase):
    
    id_lista: int
    id_producto: int


class LPPUpsert(LPPCreate):
    """Idéntico a create para un upsert lógico en router."""


class LPPOut(LPPBase):
    id_lista: int
    id_producto: int

    class Config:
        from_attributes = True


# --------- Formatos útiles para anidado ---------
class LPPWithRefsOut(LPPOut):
    """Devuelve refs (id+nombre) para ambos lados de la relación."""
    lista: ListaDePreciosRefOut
    producto: ProductoRefOut


# Mínimo para incrustar dentro de "producto con precios" o "lista con precios".
class LPPBasicOut(LPPBase):
    id_lista: int
    id_producto: int