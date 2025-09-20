from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from decimal import Decimal
from datetime import date

if TYPE_CHECKING:
    from .empresa import Empresa
    from .usuario import Usuario
    from .clienteRepartoDia import ClienteRepartoDia
    from .recorrido import Recorrido

from sqlalchemy import Integer, Date, Numeric, Text, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base

SCHEMA = "soderia"


class RepartoDia(Base):
    __tablename__ = "reparto_dia"
    __table_args__ = ({"schema": SCHEMA},)

    #PK
    id_repartodia: Mapped[int] = mapped_column(Integer, primary_key=True)

    #FKs
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.usuario.id_usuario"),
        nullable=False,
    )
    id_empresa: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.empresa.id_empresa"),
        nullable=False,
    )

    #Campos
    fecha: Mapped[date] = mapped_column(Date, nullable=False)  
    total_recaudado: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2), server_default=text("0"))
    total_efectivo: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2), server_default=text("0"))
    total_virtual: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2), server_default=text("0"))
    observacion: Mapped[Optional[str]] = mapped_column(Text)

    #Relaciones
    empresa: Mapped["Empresa"] = relationship(
        "Empresa", back_populates="repartos_dias", lazy="selectin"
    )
    usuario: Mapped["Usuario"] = relationship(
        "Usuario", back_populates="reparto_dia", lazy="selectin"
    )
    reparto_clientes: Mapped[List["ClienteRepartoDia"]] = relationship(
        "ClienteRepartoDia", back_populates="reparto_dia", lazy="selectin"
    )
    recorridos: Mapped[List["Recorrido"]] = relationship(
        "Recorrido", back_populates="reparto_dia", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<RepartoDia id={self.id_repartodia} fecha={self.fecha}>"
