from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .clienteDiaSemana import ClienteDiaSemana

from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

SCHEMA = "soderia"


class DiaSemana(Base):
    __tablename__ = "dia_semana"
    __table_args__ = (
        UniqueConstraint("nombre_dia", name="dia_semana_nombre_dia_key"),
        {"schema": SCHEMA},
    )

    # PK
    id_dia: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Campos
    nombre_dia: Mapped[str] = mapped_column(String(10), nullable=False)

    # --------- RELATIONSHIPS ---------
    clientes: Mapped[List["ClienteDiaSemana"]] = relationship(
        "ClienteDiaSemana", back_populates="dia", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<DiaSemana id={self.id_dia} nombre={self.nombre_dia}>"
