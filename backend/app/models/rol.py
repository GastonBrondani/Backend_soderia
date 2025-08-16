from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from .usuarioRol import UsuarioRol

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

SCHEMA = "soderia"


class Rol(Base):
    __tablename__ = "rol"
    __table_args__ = ({"schema": SCHEMA},)

    # PK
    id_rol: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )

    # Campos
    nombre: Mapped[str] = mapped_column(String(50), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text)

    # ---------- RELATIONSHIPS ----------
    usuarios_roles: Mapped[List["UsuarioRol"]] = relationship(
        "UsuarioRol", back_populates="rol", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Rol id={self.id_rol} nombre={self.nombre}>"
