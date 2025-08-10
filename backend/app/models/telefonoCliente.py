from sqlalchemy import Column, Integer, String, Text, ForeignKey
from database import Base

class TelefonoCliente(Base):
    __tablename__ = "telefono_cliente"
    __table_args__ = {'schema': 'soderia'}

    id_telefono = Column(Integer, primary_key=True, index=True)
    legajo = Column(Integer, nullable=False)
    nro_telefono = Column(String(20), nullable=False)
    estado = Column(String(20), nullable=False)
    observacion = Column(Text, nullable=True)

    # FK explícita opcional:
    # legajo = Column(Integer, ForeignKey("soderia.cliente.legajo"), nullable=False)
