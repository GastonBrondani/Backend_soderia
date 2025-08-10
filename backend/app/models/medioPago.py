from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class MedioPago(Base):
    __tablename__ = "medio_pago"
    __table_args__ = {'schema': 'soderia'}

    id_medio_pago = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False, unique=True)

    cajas_empresa = relationship("CajaEmpresa", back_populates="medio_pago")
    pedidos = relationship("Pedido", back_populates="medio_pago")
