from __future__ import annotations
from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .persona import Persona
    from .recorrido import Recorrido
    from .usuario import Usuario

from sqlalchemy import Integer, BigInteger, Date,ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

SCHEMA = "soderia"


class Empleado(Base):
    __tablename__ = "empleado"
    __table_args__ = ({"schema": SCHEMA},)

    #PK
    legajo: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    #Fk
    dni: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(f"{SCHEMA}.persona.dni"),
        nullable=False,                                  
    )
    #Campos
    id_usuario: Mapped[int | None] = mapped_column(Integer)      
    fecha_ingreso: Mapped[date | None] = mapped_column(Date)

    #Relaciones
    persona: Mapped["Persona"] = relationship(
        "Persona",back_populates="empleado",lazy="selectin"
    )
    
    recorrido: Mapped["Recorrido"] = relationship(
        "Recorrido", back_populates="empleado", lazy="selectin"
    )
    
    usuarios: Mapped["Usuario"] = relationship(
        "Usuario",back_populates="empleado",lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Empleado legajo={self.legajo} dni={self.dni} ingreso={self.fecha_ingreso}>"
