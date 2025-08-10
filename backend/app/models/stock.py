from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Stock(Base):
    __tablename__ = "stock"
    __table_args__ = {'schema': 'soderia'}

    id_stock = Column(Integer, primary_key=True, index=True)
    id_producto = Column(Integer, ForeignKey("soderia.producto.id_producto"), nullable=False)
    cantidad = Column(Integer, nullable=False, default=0)
    id_empresa = Column(Integer, ForeignKey("soderia.empresa.id_empresa"))

    producto = relationship("Producto", back_populates="stocks")
    empresa = relationship("Empresa", back_populates="stocks")
