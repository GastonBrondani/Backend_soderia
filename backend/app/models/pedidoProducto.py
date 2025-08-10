from sqlalchemy import Column, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class PedidoProducto(Base):
    __tablename__ = "pedido_producto"
    __table_args__ = {'schema': 'soderia'}

    id_pedido = Column(Integer, ForeignKey("soderia.pedido.id_pedido"), primary_key=True)
    id_producto = Column(Integer, ForeignKey("soderia.producto.id_producto"), primary_key=True)
    cantidad = Column(Integer, nullable=False, default=1)
    precio_unitario = Column(Numeric(10, 2), nullable=False)

    pedido = relationship("Pedido", back_populates="productos")
    producto = relationship("Producto", back_populates="pedidos")
