from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional, List

if TYPE_CHECKING:
    from .cliente import Cliente
    from .empresa import Empresa
    from .medioPago import MedioPago
    from .repartoDia import RepartoDia
    from .historico import Historico
    from .movimientoStock import MovimientoStock
    from .pedidoProducto import PedidoProducto

from sqlalchemy import (
    Integer, String, Text, Numeric, DateTime,
    ForeignKey, text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

SCHEMA = "soderia"


class Pedido(Base):
    __tablename__ = "pedido"
    __table_args__ = ({"schema": SCHEMA},)

    # PK
    id_pedido: Mapped[int] = mapped_column(Integer, primary_key=True)

    # FKs
    legajo: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(f"{SCHEMA}.cliente.legajo", name="fk_pedido_cliente"),
        nullable=False,
    )
    id_medio_pago: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey(f"{SCHEMA}.medio_pago.id_medio_pago", name="fk_pedido_medio_pago"),
        nullable=True,
    )
    id_empresa: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey(f"{SCHEMA}.empresa.id_empresa", name="fk_pedido_empresa"),
        nullable=True,
    )
    id_reparto_dia: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey(f"{SCHEMA}.reparto_dia.id_reparto_dia", name="fk_pedido_reparto_dia"),
        nullable=True,
    )

    # Campos
    fecha: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    monto_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    monto_abonado: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, server_default=text("0.00")
    )
    estado: Mapped[str] = mapped_column(String(30), nullable=False)
    observacion: Mapped[Optional[str]] = mapped_column(Text)

    # --------- RELATIONSHIPS (completas) ---------
    cliente: Mapped["Cliente"] = relationship(
        "Cliente", back_populates="pedidos", lazy="selectin"
    )
    medio_pago: Mapped[Optional["MedioPago"]] = relationship(
        "MedioPago", back_populates="pedidos", lazy="selectin"
    )
    empresa: Mapped[Optional["Empresa"]] = relationship(
        "Empresa", back_populates="pedidos", lazy="selectin"
    )
    reparto_dia: Mapped[Optional["RepartoDia"]] = relationship(
        "RepartoDia", back_populates="pedidos", lazy="selectin"
    )

    historicos: Mapped[List["Historico"]] = relationship(
        "Historico", back_populates="pedido", lazy="selectin"
    )
    movimientos_stock: Mapped[List["MovimientoStock"]] = relationship(
        "MovimientoStock", back_populates="pedido", lazy="selectin"
    )
    items: Mapped[List["PedidoProducto"]] = relationship(
        "PedidoProducto", back_populates="pedido", lazy="selectin"
    )

    def __repr__(self) -> str:
        return (
            f"<Pedido id={self.id_pedido} legajo={self.legajo} "
            f"total={self.monto_total} abonado={self.monto_abonado} estado={self.estado}>"
        )
