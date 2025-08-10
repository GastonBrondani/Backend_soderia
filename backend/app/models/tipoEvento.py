from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class TipoEvento(Base):
    __tablename__ = "tipo_evento"
    __table_args__ = {'schema': 'soderia'}

    id_evento = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)

    historicos = relationship("Historico", back_populates="tipo_evento")
