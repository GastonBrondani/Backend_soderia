from sqlalchemy import Column, Integer, String, Text, ForeignKey
from database import Base

class Cliente(Base):
    __tablename__ = "cliente"
    __table_args__ = {'schema': 'soderia'}

    legajo = Column(Integer, primary_key=True, index=True)
    id_empresa = Column(Integer, ForeignKey("soderia.empresa.id_empresa"), nullable=False)
    observacion = Column(Text, nullable=True)
    dni = Column(String(20), ForeignKey("soderia.persona.dni"), nullable=False)
