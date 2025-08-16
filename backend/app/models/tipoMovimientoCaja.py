from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .cajaEmpresa import CajaEmpresa

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

SCHEMA = "soderia"


class TipoMovimientoCaja(Base):
    __tablename__ = "tipo_movimiento_caja"
    __table_args__ = ({"schema": SCHEMA},)

    # PK (serial)
    id_tipo_movimiento: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Campos
    descripcion: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    # --------- RELATIONSHIPS ---------
    caja_empresas: Mapped[List["CajaEmpresa"]] = relationship(
        "CajaEmpresa",
        back_populates="tipo_movimiento",  # en CajaEmpresa: tipo_movimiento = relationship("TipoMovimientoCaja", back_populates="caja_empresas")
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<TipoMovimientoCaja id={self.id_tipo_movimiento} descripcion={self.descripcion}>"
