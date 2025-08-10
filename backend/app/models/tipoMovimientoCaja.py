from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class TipoMovimientoCaja(Base):
    __tablename__ = "tipo_movimiento_caja"
    __table_args__ = {'schema': 'soderia'}

    id_tipo_movimiento = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(100), nullable=False, unique=True)

    caja_empresas = relationship("CajaEmpresa", back_populates="tipo_movimiento_caja")
