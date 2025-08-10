from sqlalchemy import Column, Integer, String, Numeric, Text
from sqlalchemy.orm import relationship
from database import Base

class Producto(Base):
    __tablename__ = "producto"
    __table_args__ = {'schema': 'soderia'}

    id_producto = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    estado = Column(String(20), nullable=False)
    litros = Column(Numeric(10, 2))
    tipo_dispenser = Column(String(50))
    observacion = Column(Text)

    listas_precios = relationship("ListaPrecioProducto", back_populates="producto")
    movimientos_stock = relationship("MovimientoStock", back_populates="producto")
    pedidos_producto = relationship("PedidoProducto", back_populates="producto")
    productos_cliente = relationship("ProductoCliente", back_populates="producto")
    stock = relationship("Stock", back_populates="producto")
