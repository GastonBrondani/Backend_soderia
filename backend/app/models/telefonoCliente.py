from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .cliente import Cliente

from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

SCHEMA = "soderia"


class TelefonoCliente(Base):
    __tablename__ = "telefono_cliente"
    __table_args__ = ({"schema": SCHEMA},)

    # PK (serial)
    id_telefono: Mapped[int] = mapped_column(Integer, primary_key=True)

    # FK -> cliente.legajo
    legajo: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(f"{SCHEMA}.cliente.legajo", name="fk_telefono_cliente_cliente"),
        nullable=False,
    )

    # Campos
    nro_telefono: Mapped[str] = mapped_column(String(20), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False)
    observacion: Mapped[Optional[str]] = mapped_column(Text)

    # --------- RELATIONSHIPS (completa) ---------
    cliente: Mapped["Cliente"] = relationship(
        "Cliente",
        back_populates="telefonos",  # en Cliente: telefonos = relationship("TelefonoCliente", back_populates="cliente")
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<TelefonoCliente id={self.id_telefono} legajo={self.legajo} nro={self.nro_telefono}>"
