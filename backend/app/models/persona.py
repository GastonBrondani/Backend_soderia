from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .cliente import Cliente
    from .empleado import Empleado
    from .usuario import Usuario

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

SCHEMA = "soderia"


class Persona(Base):
    __tablename__ = "persona"
    __table_args__ = {"schema": SCHEMA}

    # PK
    dni: Mapped[str] = mapped_column(String(20), primary_key=True)

    # Campos
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)

    # --------- RELATIONSHIPS (completas) ---------
    clientes: Mapped[List["Cliente"]] = relationship(
        "Cliente", back_populates="persona", lazy="selectin"
    )
    empleados: Mapped[List["Empleado"]] = relationship(
        "Empleado", back_populates="persona", lazy="selectin"
    )
    #usuarios: Mapped[List["Usuario"]] = relationship(
    #    "Usuario", back_populates="persona", lazy="selectin"
    #)
    usuarios: Mapped[List["Usuario"]] = relationship(
        "Usuario",
        back_populates="persona",
        lazy="selectin",
        primaryjoin="Persona.dni==foreign(Usuario.dni)",
    )

    def __repr__(self) -> str:
        return f"<Persona dni={self.dni} nombre={self.nombre} apellido={self.apellido}>"
