from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .cajaEmpresa import CajaEmpresa
    from .camionReparto import CamionReparto
    from .cliente import Cliente
    from .cuentaBancariaEmpresa import CuentaBancariaEmpresa
    from .pedido import Pedido
    from .repartoDia import RepartoDia
    from .stock import Stock

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

SCHEMA = "soderia"


class Empresa(Base):
    __tablename__ = "empresa"
    __table_args__ = ({"schema": SCHEMA},)

    # PK (serial)
    id_empresa: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Campos
    razon_social: Mapped[str] = mapped_column(String(100), nullable=False)

    # --------- RELATIONSHIPS ---------
    caja_empresas: Mapped[List["CajaEmpresa"]] = relationship(
        "CajaEmpresa", back_populates="empresa", lazy="selectin"
    )
    camiones_reparto: Mapped[List["CamionReparto"]] = relationship(
        "CamionReparto", back_populates="empresa", lazy="selectin"
    )
    clientes: Mapped[List["Cliente"]] = relationship(
        "Cliente", back_populates="empresa", lazy="selectin"
    )
    cuentas_bancarias: Mapped[List["CuentaBancariaEmpresa"]] = relationship(
        "CuentaBancariaEmpresa", back_populates="empresa", lazy="selectin"
    )
    pedidos: Mapped[List["Pedido"]] = relationship(
        "Pedido", back_populates="empresa", lazy="selectin"
    )
    repartos_dia: Mapped[List["RepartoDia"]] = relationship(
        "RepartoDia", back_populates="empresa", lazy="selectin"
    )
    stocks: Mapped[List["Stock"]] = relationship(
        "Stock", back_populates="empresa", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Empresa id={self.id_empresa} razon_social={self.razon_social}>"
