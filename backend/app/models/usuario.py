from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from .cliente import Cliente
    from .empleado import Empleado
    from .persona import Persona
    from .repartoDia import RepartoDia
    from .usuarioRol import UsuarioRol

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

SCHEMA = "soderia"


class Usuario(Base):
    __tablename__ = "usuario"
    __table_args__ = ({"schema": SCHEMA},)

    # PK
    id_usuario: Mapped[int] = mapped_column(Integer, primary_key=True)

    # FK
    legajo: Mapped[int] = mapped_column(Integer, nullable=False)  
    dni: Mapped[Optional[str]] = mapped_column(String(20), unique=True)

    # Campos
    nombre_usuario: Mapped[str] = mapped_column(String(50), nullable=False)
    contraseña: Mapped[str] = mapped_column(String(100), nullable=False)

    # --------- RELATIONSHIPS ---------
    cliente: Mapped[Optional["Cliente"]] = relationship(
        "Cliente",
        back_populates="usuarios",        # en Cliente → usuarios = relationship("Usuario", back_populates="cliente")
        foreign_keys=[legajo],
        lazy="selectin",
    )

    empleado: Mapped[Optional["Empleado"]] = relationship(
        "Empleado",
        back_populates="usuarios",        # en Empleado → usuarios = relationship("Usuario", back_populates="empleado")
        foreign_keys=[legajo],
        lazy="selectin",
    )

    persona: Mapped[Optional["Persona"]] = relationship(
        "Persona",
        back_populates="usuarios",        # en Persona → usuarios = relationship("Usuario", back_populates="persona")
        foreign_keys=[dni],
        lazy="selectin",
    )

    reparto_dias: Mapped[List["RepartoDia"]] = relationship(
        "RepartoDia",
        back_populates="usuario",
        lazy="selectin",
    )

    usuario_roles: Mapped[List["UsuarioRol"]] = relationship(
        "UsuarioRol",
        back_populates="usuario",         # en UsuarioRol → usuario = relationship("Usuario", back_populates="usuario_roles")
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Usuario id={self.id_usuario} nombre_usuario={self.nombre_usuario}>"
