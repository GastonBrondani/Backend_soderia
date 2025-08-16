from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List

if TYPE_CHECKING:
    from .empresa import Empresa
    from .persona import Persona
    from .clienteCuenta import ClienteCuenta
    from .clienteDiaSemana import ClienteDiaSemana
    from .clienteRepartoDia import ClienteRepartoDia
    from .direccionCliente import DireccionCliente
    from .documentos import Documentos
    from .emailCliente import EmailCliente
    from .historico import Historico
    from .pedido import Pedido
    from .productoCliente import ProductoCliente
    from .telefonoCliente import TelefonoCliente
    from .usuario import Usuario

from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

SCHEMA = "soderia"


class Cliente(Base):
    __tablename__ = "cliente"
    __table_args__ = ({"schema": SCHEMA},)

    # PK
    legajo: Mapped[int] = mapped_column(Integer, primary_key=True)

    # FKs
    id_empresa: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.empresa.id_empresa", name="fk_cliente_empresa"),
        nullable=False,
    )
    dni: Mapped[str] = mapped_column(
        String(20),
        ForeignKey(f"{SCHEMA}.persona.dni", name="fk_cliente_persona"),
        nullable=False,
    )

    # Campos
    observacion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Many-to-one
    empresa: Mapped["Empresa"] = relationship("Empresa", lazy="selectin")
    persona: Mapped["Persona"] = relationship("Persona", lazy="selectin")

    # One-to-many (hijos que referencian Cliente)
    cuentas: Mapped[List["ClienteCuenta"]] = relationship("ClienteCuenta", lazy="selectin")
    dias_semana: Mapped[List["ClienteDiaSemana"]] = relationship("ClienteDiaSemana", lazy="selectin")
    repartos_dia: Mapped[List["ClienteRepartoDia"]] = relationship("ClienteRepartoDia", lazy="selectin")
    direcciones: Mapped[List["DireccionCliente"]] = relationship("DireccionCliente", lazy="selectin")
    documentos: Mapped[List["Documentos"]] = relationship("Documentos", lazy="selectin")
    emails: Mapped[List["EmailCliente"]] = relationship("EmailCliente", lazy="selectin")
    historicos: Mapped[List["Historico"]] = relationship("Historico", lazy="selectin")
    pedidos: Mapped[List["Pedido"]] = relationship("Pedido", lazy="selectin")
    productos: Mapped[List["ProductoCliente"]] = relationship("ProductoCliente", lazy="selectin")
    telefonos: Mapped[List["TelefonoCliente"]] = relationship("TelefonoCliente", lazy="selectin")
    #usuarios: Mapped[List["Usuario"]] = relationship("Usuario", lazy="selectin")
    usuarios: Mapped[List["Usuario"]] = relationship(
        "Usuario",
        back_populates="cliente",
        lazy="selectin",
        primaryjoin="Cliente.legajo==foreign(Usuario.legajo)",
    )

    def __repr__(self) -> str:
        return f"<Cliente legajo={self.legajo} dni={self.dni} empresa={self.id_empresa}>"

