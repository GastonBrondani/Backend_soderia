from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .cliente import Cliente

from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

SCHEMA = "soderia"


class Documentos(Base):
    __tablename__ = "documentos"
    __table_args__ = ({"schema": SCHEMA},)

    # PK (serial)
    id_documento: Mapped[int] = mapped_column(Integer, primary_key=True)

    # FK -> cliente.legajo
    legajo: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(f"{SCHEMA}.cliente.legajo", name="fk_documentos_cliente"),
        nullable=False,
    )

    # Campos
    nombre_archivo: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo_archivo: Mapped[str] = mapped_column(String(50), nullable=False)
    url_archivo: Mapped[str] = mapped_column(String(500), nullable=False)
    fecha_carga: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    observacion: Mapped[Optional[str]] = mapped_column(Text)

    # --------- RELATIONSHIPS ---------
    cliente: Mapped["Cliente"] = relationship(
        "Cliente",
        back_populates="documentos",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Documentos id={self.id_documento} legajo={self.legajo} archivo={self.nombre_archivo}>"
