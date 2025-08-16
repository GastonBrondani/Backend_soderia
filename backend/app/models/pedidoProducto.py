from __future__ import annotations
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .pedido import Pedido
    from .producto import Producto

from sqlalchemy import Integer, Numeric, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

SCHEMA = "soderia"


class PedidoProducto(Base):
    __tablename__ = "pedido_producto"
    __table_args__ = ({"schema": SCHEMA},)

    # PK compuesta: (id_pedido, id_producto)
    id_pedido: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(f"{SCHEMA}.pedido.id_pedido", name="fk_pedido_producto_pedido"),
        primary_key=True,
        nullable=False,
    )
    id_producto: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(f"{SCHEMA}.producto.id_producto", name="fk_pedido_producto_producto"),
        primary_key=True,
        nullable=False,
    )

    # Campos
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # --------- RELATIONSHIPS (completas) ---------
    pedido: Mapped["Pedido"] = relationship(
        "Pedido",
        back_populates="items",
        lazy="selectin",
    )
    producto: Mapped["Producto"] = relationship(
        "Producto",
        back_populates="pedido_items",  # en Producto: pedido_items = relationship("PedidoProducto", back_populates="producto")
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<PedidoProducto pedido={self.id_pedido} "
            f"producto={self.id_producto} cant={self.cantidad} precio={self.precio_unitario}>"
        )
