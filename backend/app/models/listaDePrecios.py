from __future__ import annotations
from datetime import date
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .listaPrecioProducto import ListaPrecioProducto

from sqlalchemy import Integer, String, Date, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

SCHEMA = "soderia"


class ListaDePrecios(Base):
    __tablename__ = "lista_de_precios"
    __table_args__ = ({"schema": SCHEMA},)

    # PK (serial)
    id_lista: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Campos
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    fecha_creacion: Mapped[date] = mapped_column(Date, nullable=False, server_default=text("CURRENT_DATE"))
    estado: Mapped[str] = mapped_column(String(20), nullable=False)

    # --------- RELATIONSHIPS ---------
    productos: Mapped[List["ListaPrecioProducto"]] = relationship(
        "ListaPrecioProducto", back_populates="lista", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<ListaDePrecios id={self.id_lista} nombre={self.nombre} estado={self.estado}>"
