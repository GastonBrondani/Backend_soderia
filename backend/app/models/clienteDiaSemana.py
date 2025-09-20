from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .cliente import Cliente
    from .diaSemana import DiaSemana

from sqlalchemy import SmallInteger, String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

SCHEMA = "soderia"


class ClienteDiaSemana(Base):
    __tablename__ = "cliente_dia_semana"
    __table_args__ = ({"schema": SCHEMA},)

    #PK
    id_cliente: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(f"{SCHEMA}.cliente.legajo"),
        primary_key=True,
        nullable=False,
    )
    id_dia: Mapped[int] = mapped_column(
        SmallInteger,
        ForeignKey(f"{SCHEMA}.dia_semana.id_dia"),
        primary_key=True,
        nullable=False,
    )

    #Campos
    turno_visita: Mapped[str | None] = mapped_column(String(20))

    #Relaciones
    cliente: Mapped["Cliente"] = relationship(
        "Cliente",back_populates="dias_semanas",lazy="selectin"
    )
    dia_semana: Mapped["DiaSemana"] = relationship(
        "DiaSemana",back_populates="clientes",lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<ClienteDiaSemana cliente={self.id_cliente} dia={self.id_dia} turno={self.turno_visita}>"
