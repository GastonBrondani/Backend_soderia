from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, model_validator


class ProductoClienteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_producto: int
    nombre: str
    cantidad: int
    estado: Optional[str] = None
    fecha_entrega: Optional[date] = None

    @model_validator(mode="before")
    @classmethod
    def _flatten(cls, data):
        if not isinstance(data, dict) and hasattr(data, "producto"):
            return {
                "id_producto": data.id_producto,
                "nombre": data.producto.nombre if data.producto else "",
                "cantidad": data.cantidad,
                "estado": data.estado,
                "fecha_entrega": data.fecha_entrega,
            }
        return data
