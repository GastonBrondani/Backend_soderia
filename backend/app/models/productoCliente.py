from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy import PrimaryKeyConstraint

from database import Base

class ProductoCliente(Base):
    __tablename__ = "producto_cliente"
    __table_args__ = (
        PrimaryKeyConstraint('id_producto', 'legajo'),
        {'schema': 'soderia'}
    )

    id_producto = Column(Integer, ForeignKey("soderia.producto.id_producto"), nullable=False)
    legajo = Column(Integer, ForeignKey("soderia.cliente.legajo"), nullable=False)
    cantidad = Column(Integer, nullable=False, default=1)
    estado = Column(String(20), nullable=False)
    fecha_entrega = Column(Date, nullable=True)
