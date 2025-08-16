from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .empresa import Empresa

from sqlalchemy import (
    Integer, String, Boolean, ForeignKey, CheckConstraint, UniqueConstraint, text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

SCHEMA = "soderia"


class CuentaBancariaEmpresa(Base):
    __tablename__ = "cuenta_bancaria_empresa"
    __table_args__ = (
        # Mantener nombres EXACTOS de constraints para que Alembic no genere diffs
        CheckConstraint(
            "tipo_cuenta IN ('CUENTA_CORRIENTE','CAJA_AHORRO','CUENTA_INVERSION')",
            name="cuenta_bancaria_empresa_tipo_cuenta_check",
        ),
        UniqueConstraint("cbu", name="cuenta_bancaria_empresa_cbu_key"),
        {"schema": SCHEMA},
    )

    # PK (serial)
    id_cuenta: Mapped[int] = mapped_column(Integer, primary_key=True)

    # FK -> empresa.id_empresa
    id_empresa: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(f"{SCHEMA}.empresa.id_empresa", name="fk_cuenta_empresa"),
        nullable=False,
    )

    # Campos
    titular_cuenta: Mapped[str] = mapped_column(String(100), nullable=False)
    cbu: Mapped[str] = mapped_column(String(22), nullable=False)  # UNIQUE por constraint
    alias: Mapped[Optional[str]] = mapped_column(String(50))
    numero_de_cuenta: Mapped[str] = mapped_column(String(20), nullable=False)
    tipo_cuenta: Mapped[str] = mapped_column(String(30), nullable=False)
    banco: Mapped[str] = mapped_column(String(50), nullable=False)
    activa: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    # --------- RELATIONSHIPS (completas para esta tabla) ---------
    empresa: Mapped["Empresa"] = relationship("Empresa", lazy="selectin")

    def __repr__(self) -> str:
        return f"<CuentaBancariaEmpresa id={self.id_cuenta} empresa={self.id_empresa} cbu={self.cbu}>"
