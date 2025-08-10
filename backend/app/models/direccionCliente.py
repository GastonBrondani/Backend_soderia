from sqlalchemy import Column, Integer, String, Text, ForeignKey
from database import Base

class DireccionCliente(Base):
    __tablename__ = "direccion_cliente"
    __table_args__ = {'schema': 'soderia'}

    id_direccion = Column(Integer, primary_key=True, index=True)
    legajo = Column(Integer, nullable=False)
    direccion = Column(String(200), nullable=False)
    zona = Column(String(100), nullable=True)
    entre_calle_1 = Column(String(100), nullable=True)
    entre_calle_2 = Column(String(100), nullable=True)
    observacion = Column(Text, nullable=True)
    tipo = Column(String(50), nullable=True)
    longitud_latitud = Column(String(100), nullable=True)
    localidad = Column(String(100), nullable=False)

    # ForeignKey si querés agregarlo como referencia:
    # legajo = Column(Integer, ForeignKey("soderia.cliente.legajo"), nullable=False)
