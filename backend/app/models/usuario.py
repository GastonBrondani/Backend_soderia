from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from .cliente import Cliente
    from .empleado import Empleado
    from .repartoDia import RepartoDia
    from .usuarioRol import UsuarioRol

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base

SCHEMA = "soderia"


class Usuario(Base):
    __tablename__ = "usuario"
    __table_args__ = ({"schema": SCHEMA},)

    #PK
    id_usuario: Mapped[int] = mapped_column(Integer, primary_key=True)

    #Campos
    nombre_usuario: Mapped[str] = mapped_column(String(100), nullable=False)
    contraseña: Mapped[str] = mapped_column(String(255), nullable=False)

    #FKs
    legajo_empleado: Mapped[Optional[int]] = mapped_column(
        ForeignKey(f"{SCHEMA}.empleado.legajo")
    )
    legajo_cliente: Mapped[Optional[int]] = mapped_column(
        ForeignKey(f"{SCHEMA}.cliente.legajo")
    )

    #Relaciones
    empleado: Mapped["Empleado"] = relationship(
        "Empleado",back_populates="usuarios",lazy="selectin"
    )

    cliente: Mapped["Cliente"] = relationship(
        "Cliente",back_populates="usuario",lazy="selectin"
    )

    reparto_dia: Mapped["RepartoDia"] = relationship(
        "RepartoDia", back_populates="usuario", lazy="selectin"
    )

    usuario_roles: Mapped[List["UsuarioRol"]] = relationship(
        "UsuarioRol",back_populates="usuario",lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Usuario id={self.id_usuario} nombre_usuario={self.nombre_usuario}>"
