from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .cajaEmpresa import CajaEmpresa
    from .pedido import Pedido

from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

SCHEMA = "soderia"


class MedioPago(Base):
    __tablename__ = "medio_pago"
    __table_args__ = (
        UniqueConstraint("nombre", name="medio_pago_nombre_key"),
        {"schema": SCHEMA},
    )

    # PK (serial)
    id_medio_pago: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Campos
    nombre: Mapped[str] = mapped_column(String(50), nullable=False)

    # --------- RELATIONSHIPS (completas) ---------
    caja_empresas: Mapped[List["CajaEmpresa"]] = relationship(
        "CajaEmpresa", back_populates="medio_pago", lazy="selectin"
    )
    pedidos: Mapped[List["Pedido"]] = relationship(
        "Pedido", back_populates="medio_pago", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<MedioPago id={self.id_medio_pago} nombre={self.nombre}>"
