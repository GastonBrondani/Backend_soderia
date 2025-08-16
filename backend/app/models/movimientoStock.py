from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .producto import Producto
    from .recorrido import Recorrido
    from .pedido import Pedido

from sqlalchemy import (
    Integer, String, Text, DateTime,
    ForeignKey, CheckConstraint, text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

SCHEMA = "soderia"


class MovimientoStock(Base):
    __tablename__ = "movimiento_stock"
    __table_args__ = (
        CheckConstraint(
            "tipo_movimiento IN ('ENTRADA','SALIDA','AJUSTE','TRASPASO')",
            name="movimiento_stock_tipo_movimiento_check",
        ),
        {"schema": SCHEMA},
    )

    # PK (serial)
    id_movimiento_stock: Mapped[int] = mapped_column(Integer, primary_key=True)

    # FKs
    id_producto: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(f"{SCHEMA}.producto.id_producto", name="fk_movimiento_producto", ondelete="RESTRICT"),
        nullable=False,
    )
    id_recorrido: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey(f"{SCHEMA}.recorrido.id_recorrido", name="fk_movimiento_recorrido", ondelete="SET NULL"),
        nullable=True,
    )
    id_pedido: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey(f"{SCHEMA}.pedido.id_pedido", name="fk_movimiento_pedido", ondelete="SET NULL"),
        nullable=True,
    )

    # Campos
    fecha: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    tipo_movimiento: Mapped[str] = mapped_column(String(20), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    observacion: Mapped[Optional[str]] = mapped_column(Text)

    # --------- RELATIONSHIPS (completas para esta tabla) ---------
    producto: Mapped["Producto"] = relationship(
        "Producto", back_populates="movimientos_stock", lazy="selectin"
    )
    recorrido: Mapped[Optional["Recorrido"]] = relationship(
        "Recorrido", back_populates="movimientos_stock", lazy="selectin"
    )
    pedido: Mapped[Optional["Pedido"]] = relationship(
        "Pedido", back_populates="movimientos_stock", lazy="selectin"
    )

    def __repr__(self) -> str:
        return (
            f"<MovimientoStock id={self.id_movimiento_stock} prod={self.id_producto} "
            f"tipo={self.tipo_movimiento} cant={self.cantidad}>"
        )
