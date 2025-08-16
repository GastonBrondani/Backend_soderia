from __future__ import annotations
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .cliente import Cliente

from sqlalchemy import Integer, String, Numeric, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

SCHEMA = "soderia"


class ClienteCuenta(Base):
    __tablename__ = "cliente_cuenta"
    __table_args__ = ({"schema": SCHEMA},)

    # PK
    id_cuenta: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )

    # FK -> cliente.legajo
    legajo: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.cliente.legajo", name="fk_cliente_cuenta_cliente"),
        nullable=False,
    )

    # Campos
    saldo: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, server_default=text("0.00")
    )
    deuda: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, server_default=text("0.00")
    )
    estado: Mapped[str] = mapped_column(String(20), nullable=False)
    tipo_de_cuenta: Mapped[str] = mapped_column(String(30), nullable=False)
    numero_bidones: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )

    # --------- RELATIONSHIPS ---------
    cliente: Mapped["Cliente"] = relationship("Cliente", back_populates="cuentas", lazy="selectin")

    def __repr__(self) -> str:
        return f"<ClienteCuenta id={self.id_cuenta} legajo={self.legajo} saldo={self.saldo} deuda={self.deuda}>"
