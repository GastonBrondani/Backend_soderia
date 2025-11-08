from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .cajaEmpresa import CajaEmpresa
    from .pedido import Pedido

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

#SCHEMA = "soderia"


class MedioPago(Base):
    __tablename__ = "medio_pago"
    #__table_args__ = {"schema": SCHEMA}

    #PK
    id_medio_pago: Mapped[int] = mapped_column(Integer, primary_key=True)

    #Campos
    nombre: Mapped[str] = mapped_column(String(50), nullable=False)

    #Relaciones
    caja_empresa: Mapped["CajaEmpresa"] = relationship(
        "CajaEmpresa", back_populates="medio_pago", lazy="selectin"
    )
    pedido: Mapped["Pedido"] = relationship(
        "Pedido", back_populates="medio_pagos", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<MedioPago id={self.id_medio_pago} nombre={self.nombre}>"
