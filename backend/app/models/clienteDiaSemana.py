from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .cliente import Cliente
    from .diaSemana import DiaSemana

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

SCHEMA = "soderia"


class ClienteDiaSemana(Base):
    __tablename__ = "cliente_dia_semana"
    __table_args__ = ({"schema": SCHEMA},)

    # PK compuesta (id_cliente, id_dia)
    id_cliente: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(f"{SCHEMA}.cliente.legajo", name="fk_cliente_dia_cliente"),
        primary_key=True,
    )
    id_dia: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(f"{SCHEMA}.dia_semana.id_dia", name="fk_cliente_dia_dia_semana"),
        primary_key=True,
    )

    # Campos
    turno_visita: Mapped[str] = mapped_column(String(20), nullable=False)

    # --------- RELATIONSHIPS ---------
    cliente: Mapped["Cliente"] = relationship("Cliente", lazy="selectin")
    dia: Mapped["DiaSemana"] = relationship("DiaSemana", lazy="selectin")

    def __repr__(self) -> str:
        return f"<ClienteDiaSemana cliente={self.id_cliente} dia={self.id_dia} turno={self.turno_visita}>"
