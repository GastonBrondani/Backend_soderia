from sqlalchemy import Column, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class ListaPrecioProducto(Base):
    __tablename__ = "lista_precio_producto"
    __table_args__ = {'schema': 'soderia'}

    id_lista = Column(Integer, ForeignKey("soderia.lista_de_precios.id_lista"), primary_key=True)
    id_producto = Column(Integer, ForeignKey("soderia.producto.id_producto"), primary_key=True)
    precio = Column(Numeric(10, 2), nullable=False)

    lista_de_precios = relationship("ListaDePrecios", back_populates="productos")
    producto = relationship("Producto", back_populates="listas_precios")
