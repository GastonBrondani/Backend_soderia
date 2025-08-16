from __future__ import annotations
from datetime import date
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .persona import Persona
    from .recorrido import Recorrido
    from .usuario import Usuario

from sqlalchemy import Integer, String, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

SCHEMA = "soderia"


class Empleado(Base):
    __tablename__ = "empleado"
    __table_args__ = ({"schema": SCHEMA},)

    # PK (serial)
    legajo: Mapped[int] = mapped_column(Integer, primary_key=True)

    # FK a persona.dni
    dni: Mapped[str] = mapped_column(
        String(20),
        ForeignKey(f"{SCHEMA}.persona.dni", name="fk_empleado_persona"),
        nullable=False,
    )

    # Campos
    id_usuario: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha_ingreso: Mapped[date] = mapped_column(Date, nullable=False)

    # --------- RELATIONSHIPS ---------
    persona: Mapped["Persona"] = relationship("Persona", lazy="selectin")

    recorridos: Mapped[list["Recorrido"]] = relationship(
        "Recorrido", back_populates="empleado", lazy="selectin"
    )

    #usuarios: Mapped[list["Usuario"]] = relationship(
    #    "Usuario", back_populates="empleado", lazy="selectin"
    #)
    usuarios: Mapped[List["Usuario"]] = relationship(
        "Usuario",
        back_populates="empleado",
        lazy="selectin",
        primaryjoin="Empleado.legajo==foreign(Usuario.legajo)",
    )

    def __repr__(self) -> str:
        return f"<Empleado legajo={self.legajo} dni={self.dni} ingreso={self.fecha_ingreso}>"
