from sqlalchemy import Column, Integer, String, Numeric, Text, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy import PrimaryKeyConstraint

from database import Base

class ClienteRepartoDia(Base):
    __tablename__ = "cliente_reparto_dia"
    __table_args__ = (
        PrimaryKeyConstraint('id_reparto_dia', 'legajo'),
        {'schema': 'soderia'}
    )

    legajo = Column(Integer, ForeignKey("soderia.cliente.legajo"), nullable=False)
    bidones_entregados = Column(Integer, nullable=False, default=0)
    monto_abonado = Column(Numeric(10, 2), nullable=False, default=0.00)
    estado_visita = Column(String(30), nullable=False)
    turno_visita = Column(String(20), nullable=False)
    observacion = Column(Text, nullable=True)
    id_reparto_dia = Column(Integer, ForeignKey("soderia.reparto_dia.id_reparto_dia"), nullable=False)
