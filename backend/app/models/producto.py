from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from decimal import Decimal

if TYPE_CHECKING:
    from .listaPrecioProducto import ListaPrecioProducto
    from .movimientoStock import MovimientoStock
    from .pedidoProducto import PedidoProducto
    from .productoCliente import ProductoCliente
    from .stock import Stock

from sqlalchemy import Integer, String, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

SCHEMA = "soderia"


class Producto(Base):
    __tablename__ = "producto"
    __table_args__ = {"schema": SCHEMA}

    # PK
    id_producto: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Campos
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False)
    litros: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    tipo_dispenser: Mapped[Optional[str]] = mapped_column(String(50))
    observacion: Mapped[Optional[str]] = mapped_column(Text)

    # --------- RELATIONSHIPS (completas) ---------
    lista_precios: Mapped[List["ListaPrecioProducto"]] = relationship(
        "ListaPrecioProducto", back_populates="producto", lazy="selectin"
    )
    movimientos_stock: Mapped[List["MovimientoStock"]] = relationship(
        "MovimientoStock", back_populates="producto", lazy="selectin"
    )
    pedidos_producto: Mapped[List["PedidoProducto"]] = relationship(
        "PedidoProducto", back_populates="producto", lazy="selectin"
    )
    productos_cliente: Mapped[List["ProductoCliente"]] = relationship(
        "ProductoCliente", back_populates="producto", lazy="selectin"
    )
    stocks: Mapped[List["Stock"]] = relationship(
        "Stock", back_populates="producto", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Producto id={self.id_producto} nombre={self.nombre} estado={self.estado}>"
