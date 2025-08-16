from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .usuario import Usuario
    from .rol import Rol

from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

SCHEMA = "soderia"


class UsuarioRol(Base):
    __tablename__ = "usuario_rol"
    __table_args__ = ({"schema": SCHEMA},)

    # PK compuesta (¡mismo orden que en la DB!): (id_rol, id_usuario)
    id_rol: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(f"{SCHEMA}.rol.id_rol", name="fk_usuario_rol_rol"),
        primary_key=True,
        nullable=False,
    )
    id_usuario: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(f"{SCHEMA}.usuario.id_usuario", name="fk_usuario_rol_usuario"),
        primary_key=True,
        nullable=False,
    )

    # --------- RELATIONSHIPS ---------
    rol: Mapped["Rol"] = relationship("Rol", back_populates="usuarios_roles", lazy="selectin")
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="usuario_roles", lazy="selectin")

    def __repr__(self) -> str:
        return f"<UsuarioRol rol={self.id_rol} usuario={self.id_usuario}>"
