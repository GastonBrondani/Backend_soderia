from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from database import Base

class Documentos(Base):
    __tablename__ = "documentos"
    __table_args__ = {'schema': 'soderia'}

    id_documento = Column(Integer, primary_key=True, index=True)
    legajo = Column(Integer, nullable=False)
    nombre_archivo = Column(String(255), nullable=False)
    tipo_archivo = Column(String(50), nullable=False)
    url_archivo = Column(String(500), nullable=False)
    fecha_carga = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    observacion = Column(Text, nullable=True)

    # FK explícita opcional:
    # legajo = Column(Integer, ForeignKey("soderia.cliente.legajo"), nullable=False)
