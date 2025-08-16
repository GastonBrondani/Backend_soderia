from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .cliente import Cliente
    from .pedido import Pedido
    from .tipoEvento import TipoEvento

from sqlalchemy import Integer, Text, DateTime, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

SCHEMA = "soderia"


class Historico(Base):
    __tablename__ = "historico"
    __table_args__ = ({"schema": SCHEMA},)

    # PK (serial)
    id_historico: Mapped[int] = mapped_column(Integer, primary_key=True)

    # FKs
    legajo: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(f"{SCHEMA}.cliente.legajo", name="fk_historico_cliente"),
        nullable=False,
    )
    id_evento: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(f"{SCHEMA}.tipo_evento.id_evento", name="fk_historico_tipo_evento"),
        nullable=False,
    )
    id_pedido: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey(f"{SCHEMA}.pedido.id_pedido", name="fk_historico_pedido", ondelete="SET NULL"),
        nullable=True,
    )

    # Campos
    fecha: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    observacion: Mapped[Optional[str]] = mapped_column(Text)

    # --------- RELATIONSHIPS ---------
    cliente: Mapped["Cliente"] = relationship("Cliente", back_populates="historicos", lazy="selectin")
    evento: Mapped["TipoEvento"] = relationship("TipoEvento", lazy="selectin")
    pedido: Mapped[Optional["Pedido"]] = relationship("Pedido", back_populates="historicos", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Historico id={self.id_historico} legajo={self.legajo} evento={self.id_evento} fecha={self.fecha}>"
