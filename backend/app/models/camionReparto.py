from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .empresa import Empresa
    from .recorrido import Recorrido

from sqlalchemy import String, Integer, Boolean, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

SCHEMA = "soderia"


class CamionReparto(Base):
    __tablename__ = "camion_reparto"
    __table_args__ = ({"schema": SCHEMA},)

    # PK
    patente: Mapped[str] = mapped_column(String(10), primary_key=True)

    # FK -> empresa.id_empresa
    id_empresa: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.empresa.id_empresa", name="fk_camion_empresa"),
        nullable=False,
    )

    # activo boolean default true
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    # --------- RELATIONSHIPS (completas) ---------
    # many-to-one -> Empresa
    empresa: Mapped["Empresa"] = relationship(
        "Empresa",
        back_populates="camiones_reparto",
        lazy="selectin",
    )

    # one-to-many <- Recorrido (FK recorrido.patente -> camion_reparto.patente)
    recorridos: Mapped[List["Recorrido"]] = relationship(
        "Recorrido",
        back_populates="camion",
        lazy="selectin",
        cascade="all, delete-orphan",  # quita esta línea si no querés borrar recorridos al borrar el camión
        passive_deletes=False,
    )

    def __repr__(self) -> str:
        return f"<CamionReparto patente={self.patente} empresa={self.id_empresa} activo={self.activo}>"
