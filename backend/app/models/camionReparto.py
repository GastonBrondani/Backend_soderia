from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class CamionReparto(Base):
    __tablename__ = "camion_reparto"
    __table_args__ = {'schema': 'soderia'}

    patente = Column(String(10), primary_key=True, index=True)
    id_empresa = Column(Integer, ForeignKey("soderia.empresa.id_empresa"), nullable=False)
    activo = Column(Boolean, nullable=False, default=True)

    empresa = relationship("Empresa", back_populates="camiones")
    recorridos = relationship("Recorrido", back_populates="camion")
