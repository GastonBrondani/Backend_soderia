from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .historico import Historico

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

SCHEMA = "soderia"


class TipoEvento(Base):
    __tablename__ = "tipo_evento"
    __table_args__ = ({"schema": SCHEMA},)

    # PK (serial)
    id_evento: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Campos
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

    # --------- RELATIONSHIPS (completa) ---------
    historicos: Mapped[List["Historico"]] = relationship(
        "Historico",
        back_populates="tipo_evento",  # en Historico: tipo_evento = relationship("TipoEvento", back_populates="historicos")
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<TipoEvento id={self.id_evento} nombre={self.nombre}>"
