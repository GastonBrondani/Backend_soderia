from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .empresa import Empresa
    from .tipoMovimientoCaja import TipoMovimientoCaja
    from .medioPago import MedioPago

from sqlalchemy import (
    Integer, String, Text, Numeric, DateTime, CheckConstraint, ForeignKey, text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

SCHEMA = "soderia"


class CajaEmpresa(Base):
    __tablename__ = "caja_empresa"
    __table_args__ = (
        CheckConstraint("tipo IN ('INGRESO', 'EGRESO')", name="caja_empresa_tipo_check"),
        {"schema": SCHEMA},
    )

    # PK (serial en DB con nextval de la secuencia)
    id_caja_empresa: Mapped[int] = mapped_column(Integer, primary_key=True)

    # FKs (nombres EXACTOS como en la DB)
    id_empresa: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.empresa.id_empresa", name="fk_caja_empresa_empresa"),
        nullable=False,
    )
    id_tipo_movimiento: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.tipo_movimiento_caja.id_tipo_movimiento", name="fk_caja_tipo_movimiento"),
        nullable=False,
    )
    id_medio_pago: Mapped[Optional[int]] = mapped_column(
        ForeignKey(f"{SCHEMA}.medio_pago.id_medio_pago", name="fk_caja_medio_pago"),
        nullable=True,
    )

    # Campos
    fecha: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    tipo: Mapped[str] = mapped_column(String(10), nullable=False)  # 'INGRESO' | 'EGRESO'
    monto: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    observacion: Mapped[Optional[str]] = mapped_column(Text)

    # RELATIONSHIPS (completas para esta tabla: solo many-to-one)
    empresa: Mapped["Empresa"] = relationship("Empresa", lazy="selectin")
    tipo_movimiento: Mapped["TipoMovimientoCaja"] = relationship("TipoMovimientoCaja", lazy="selectin")
    medio_pago: Mapped[Optional["MedioPago"]] = relationship("MedioPago", lazy="selectin")

    def __repr__(self) -> str:
        return f"<CajaEmpresa id={self.id_caja_empresa} tipo={self.tipo} monto={self.monto}>"
