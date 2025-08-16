from __future__ import annotations
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .cliente import Cliente
    from .repartoDia import RepartoDia

from sqlalchemy import Integer, String, Text, Numeric, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

SCHEMA = "soderia"


class ClienteRepartoDia(Base):
    __tablename__ = "cliente_reparto_dia"
    __table_args__ = ({"schema": SCHEMA},)

    # PK compuesta: (id_reparto_dia, legajo)
    id_reparto_dia: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(f"{SCHEMA}.reparto_dia.id_reparto_dia", name="fk_cliente_reparto_dia"),
        primary_key=True,
    )
    legajo: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(f"{SCHEMA}.cliente.legajo", name="fk_cliente_reparto_cliente"),
        primary_key=True,
    )

    # Campos
    bidones_entregados: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    monto_abonado: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, server_default=text("0.00")
    )
    estado_visita: Mapped[str] = mapped_column(String(30), nullable=False)
    turno_visita: Mapped[str] = mapped_column(String(20), nullable=False)
    observacion: Mapped[Optional[str]] = mapped_column(Text)

    # --------- RELATIONSHIPS (completas para esta tabla) ---------
    cliente: Mapped["Cliente"] = relationship("Cliente", lazy="selectin")
    reparto_dia: Mapped["RepartoDia"] = relationship("RepartoDia", lazy="selectin")

    def __repr__(self) -> str:
        return (
            f"<ClienteRepartoDia reparto={self.id_reparto_dia} "
            f"legajo={self.legajo} estado={self.estado_visita} turno={self.turno_visita}>"
        )
