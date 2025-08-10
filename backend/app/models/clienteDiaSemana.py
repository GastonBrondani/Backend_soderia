from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy import PrimaryKeyConstraint

from database import Base

class ClienteDiaSemana(Base):
    __tablename__ = "cliente_dia_semana"
    __table_args__ = (
        PrimaryKeyConstraint('id_cliente', 'id_dia'),
        {'schema': 'soderia'}
    )

    id_cliente = Column(Integer, ForeignKey("soderia.cliente.legajo"), nullable=False)
    id_dia = Column(Integer, ForeignKey("soderia.dia_semana.id_dia"), nullable=False)
    turno_visita = Column(String(20), nullable=False)
