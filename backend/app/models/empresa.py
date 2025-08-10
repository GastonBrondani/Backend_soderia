from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class Empresa(Base):
    __tablename__ = "empresa"
    __table_args__ = {'schema': 'soderia'}

    id_empresa = Column(Integer, primary_key=True, index=True)
    razon_social = Column(String(100), nullable=False)

    # Relaciones hacia las tablas que referencian a empresa
    caja_empresas = relationship("CajaEmpresa", back_populates="empresa")
    camion_repartos = relationship("CamionReparto", back_populates="empresa")
    clientes = relationship("Cliente", back_populates="empresa")
    cuenta_bancaria_empresas = relationship("CuentaBancariaEmpresa", back_populates="empresa")
    pedidos = relationship("Pedido", back_populates="empresa")
    reparto_dias = relationship("RepartoDia", back_populates="empresa")
    stocks = relationship("Stock", back_populates="empresa")
