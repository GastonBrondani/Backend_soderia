from __future__ import annotations
from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .producto import Producto
    from .cliente import Cliente

from sqlalchemy import Integer, String, Date, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

SCHEMA = "soderia"


class ProductoCliente(Base):
    __tablename__ = "producto_cliente"
    __table_args__ = ({"schema": SCHEMA},)

    # PK compuesta: (id_producto, legajo)
    id_producto: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(f"{SCHEMA}.producto.id_producto", name="fk_producto_cliente_producto"),
        primary_key=True,
        nullable=False,
    )
    legajo: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(f"{SCHEMA}.cliente.legajo", name="fk_producto_cliente_cliente"),
        primary_key=True,
        nullable=False,
    )

    # Campos
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    estado: Mapped[str] = mapped_column(String(20), nullable=False)
    fecha_entrega: Mapped[date | None] = mapped_column(Date)

    # --------- RELATIONSHIPS (completas) ---------
    producto: Mapped["Producto"] = relationship(
        "Producto",
        back_populates="productos_cliente",   # en Producto: productos_cliente = relationship("ProductoCliente", back_populates="producto")
        lazy="selectin",
    )
    cliente: Mapped["Cliente"] = relationship(
        "Cliente",
        back_populates="productos",           # en Cliente: productos = relationship("ProductoCliente", back_populates="cliente")
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<ProductoCliente prod={self.id_producto} legajo={self.legajo} cant={self.cantidad} estado={self.estado}>"
