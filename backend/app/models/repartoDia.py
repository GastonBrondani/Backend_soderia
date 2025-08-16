from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from decimal import Decimal
from datetime import date

if TYPE_CHECKING:
    from .empresa import Empresa
    from .usuario import Usuario
    from .clienteRepartoDia import ClienteRepartoDia
    from .pedido import Pedido
    from .recorrido import Recorrido

from sqlalchemy import Integer, Date, Numeric, Text, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

SCHEMA = "soderia"


class RepartoDia(Base):
    __tablename__ = "reparto_dia"
    __table_args__ = ({"schema": SCHEMA},)

    # PK
    id_reparto_dia: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )

    # Campos
    fecha: Mapped[date] = mapped_column(
        Date, nullable=False, server_default=text("CURRENT_DATE")
    )
    total_recaudado: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, server_default=text("0.00")
    )
    total_efectivo: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, server_default=text("0.00")
    )
    total_virtual: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, server_default=text("0.00")
    )
    observacion: Mapped[Optional[str]] = mapped_column(Text)

    # FKs
    id_usuario: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey(f"{SCHEMA}.usuario.id_usuario", name="fk_reparto_usuario", ondelete="SET NULL"),
        nullable=True,
    )
    id_empresa: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey(f"{SCHEMA}.empresa.id_empresa", name="fk_reparto_empresa"),
        nullable=True,
    )

    # ---------- RELATIONSHIPS ----------
    empresa: Mapped[Optional["Empresa"]] = relationship(
        "Empresa", back_populates="repartos_dia", lazy="selectin"
    )    

    clientes_reparto: Mapped[List["ClienteRepartoDia"]] = relationship(
        "ClienteRepartoDia", back_populates="reparto_dia", lazy="selectin"
    )
    pedidos: Mapped[List["Pedido"]] = relationship(
        "Pedido", back_populates="reparto_dia", lazy="selectin"
    )
    recorridos: Mapped[List["Recorrido"]] = relationship(
        "Recorrido", back_populates="reparto_dia", lazy="selectin"
    )
    usuario: Mapped["Usuario | None"] = relationship(
        "Usuario",
        back_populates="reparto_dias",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<RepartoDia id={self.id_reparto_dia} fecha={self.fecha}>"
