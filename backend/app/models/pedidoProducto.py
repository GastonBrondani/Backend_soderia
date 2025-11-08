from __future__ import annotations
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .pedido import Pedido
    from .producto import Producto

from sqlalchemy import Integer, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

#SCHEMA = "soderia"


class PedidoProducto(Base):
    __tablename__ = "pedido_producto"
    #__table_args__ = ({"schema": SCHEMA},)

    #PKs
    id_pedido: Mapped[int] = mapped_column(
        ForeignKey("pedido.id_pedido"),
        primary_key=True,
        nullable=False,
    )
    id_producto: Mapped[int] = mapped_column(
        ForeignKey("producto.id_producto"),
        primary_key=True,
        nullable=False,
    )

    #Campos
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    #Relaciones
    pedido: Mapped["Pedido"] = relationship(
        "Pedido", back_populates="pedidos_productos", lazy="selectin"
    )
    producto: Mapped["Producto"] = relationship(
        "Producto", back_populates="pedidos_productos", lazy="selectin"
    )

    def __repr__(self) -> str:
        return (
            f"<PedidoProducto pedido={self.id_pedido} "
            f"producto={self.id_producto} cant={self.cantidad} "
            f"precio={self.precio_unitario}>"
        )
