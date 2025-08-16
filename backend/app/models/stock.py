from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .producto import Producto
    from .empresa import Empresa

from sqlalchemy import Integer, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

SCHEMA = "soderia"


class Stock(Base):
    __tablename__ = "stock"
    __table_args__ = ({"schema": SCHEMA},)

    # PK (serial)
    id_stock: Mapped[int] = mapped_column(Integer, primary_key=True)

    # FKs
    id_producto: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(f"{SCHEMA}.producto.id_producto", name="fk_stock_producto"),
        nullable=False,
    )
    id_empresa: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey(f"{SCHEMA}.empresa.id_empresa", name="fk_stock_empresa"),
        nullable=True,
    )

    # Campos
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))

    # --------- RELATIONSHIPS (completas) ---------
    producto: Mapped["Producto"] = relationship(
        "Producto", back_populates="stocks", lazy="selectin"
    )
    empresa: Mapped[Optional["Empresa"]] = relationship(
        "Empresa", back_populates="stocks", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Stock id={self.id_stock} prod={self.id_producto} emp={self.id_empresa} cant={self.cantidad}>"
