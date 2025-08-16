from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .cliente import Cliente

from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

SCHEMA = "soderia"


class EmailCliente(Base):
    __tablename__ = "email_cliente"
    __table_args__ = ({"schema": SCHEMA},)

    # PK (serial)
    id_email: Mapped[int] = mapped_column(Integer, primary_key=True)

    # FK -> cliente.legajo
    legajo: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(f"{SCHEMA}.cliente.legajo", name="fk_email_cliente_cliente"),
        nullable=False,
    )

    # Campos
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False)
    observacion: Mapped[Optional[str]] = mapped_column(Text)

    # --------- RELATIONSHIPS ---------
    cliente: Mapped["Cliente"] = relationship(
        "Cliente",
        back_populates="emails",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<EmailCliente id={self.id_email} legajo={self.legajo} email={self.email}>"
