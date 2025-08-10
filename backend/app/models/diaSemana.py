from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class DiaSemana(Base):
    __tablename__ = "dia_semana"
    __table_args__ = {'schema': 'soderia'}

    id_dia = Column(Integer, primary_key=True, index=True)
    nombre_dia = Column(String(10), nullable=False, unique=True)

    clientes_dias = relationship("ClienteDiaSemana", back_populates="dia_semana")
