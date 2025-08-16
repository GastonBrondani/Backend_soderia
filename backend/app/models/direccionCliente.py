from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .cliente import Cliente

from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

SCHEMA = "soderia"


class DireccionCliente(Base):
    __tablename__ = "direccion_cliente"
    __table_args__ = ({"schema": SCHEMA},)

    # PK (serial)
    id_direccion: Mapped[int] = mapped_column(Integer, primary_key=True)

    # FK -> cliente.legajo
    legajo: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(f"{SCHEMA}.cliente.legajo", name="fk_direccion_cliente_cliente"),
        nullable=False,
    )

    # Campos
    direccion: Mapped[str] = mapped_column(String(200), nullable=False)
    zona: Mapped[Optional[str]] = mapped_column(String(100))
    entre_calle_1: Mapped[Optional[str]] = mapped_column(String(100))
    entre_calle_2: Mapped[Optional[str]] = mapped_column(String(100))
    observacion: Mapped[Optional[str]] = mapped_column(Text)
    tipo: Mapped[Optional[str]] = mapped_column(String(50))
    longitud_latitud: Mapped[Optional[str]] = mapped_column(String(100))
    localidad: Mapped[str] = mapped_column(String(100), nullable=False)

    # --------- RELATIONSHIPS (completa) ---------
    cliente: Mapped["Cliente"] = relationship(
        "Cliente",
        back_populates="direcciones",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<DireccionCliente id={self.id_direccion} legajo={self.legajo} {self.direccion}>"
