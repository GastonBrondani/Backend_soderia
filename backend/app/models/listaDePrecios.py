from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from database import Base

class ListaDePrecios(Base):
    __tablename__ = "lista_de_precios"
    __table_args__ = {'schema': 'soderia'}

    id_lista = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    fecha_creacion = Column(Date, nullable=False)
    estado = Column(String(20), nullable=False)

    productos = relationship("ListaPrecioProducto", back_populates="lista_de_precios")
