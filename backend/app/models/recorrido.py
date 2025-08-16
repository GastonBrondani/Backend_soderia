from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from decimal import Decimal

if TYPE_CHECKING:
    from .empleado import Empleado
    from .repartoDia import RepartoDia
    from .camionReparto import CamionReparto
    from .movimientoStock import MovimientoStock

from sqlalchemy import Integer, String, Numeric, Text, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

SCHEMA = "soderia"


class Recorrido(Base):
    __tablename__ = "recorrido"
    __table_args__ = ({"schema": SCHEMA},)

    # PK (serial)
    id_recorrido: Mapped[int] = mapped_column(Integer, primary_key=True)

    # FKs
    id_empleado: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(f"{SCHEMA}.empleado.legajo", name="fk_recorrido_empleado"),
        nullable=False,
    )
    id_reparto_dia: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(f"{SCHEMA}.reparto_dia.id_reparto_dia", name="fk_recorrido_reparto_dia"),
        nullable=False,
    )
    patente: Mapped[str] = mapped_column(
        String(10),
        ForeignKey(f"{SCHEMA}.camion_reparto.patente", name="fk_recorrido_camion"),
        nullable=False,
    )

    # Campos
    dinero_inicial: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, server_default=text("0.00")
    )
    stock_inicial: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    observacion: Mapped[Optional[str]] = mapped_column(Text)

    # --------- RELATIONSHIPS (completas) ---------
    empleado: Mapped["Empleado"] = relationship(
        "Empleado", back_populates="recorridos", lazy="selectin"
    )
    reparto_dia: Mapped["RepartoDia"] = relationship(
        "RepartoDia", back_populates="recorridos", lazy="selectin"
    )
    camion: Mapped["CamionReparto"] = relationship(
        "CamionReparto", back_populates="recorridos", lazy="selectin"
    )

    movimientos_stock: Mapped[List["MovimientoStock"]] = relationship(
        "MovimientoStock", back_populates="recorrido", lazy="selectin"
    )

    def __repr__(self) -> str:
        return (
            f"<Recorrido id={self.id_recorrido} emp={self.id_empleado} "
            f"reparto={self.id_reparto_dia} patente={self.patente}>"
        )
