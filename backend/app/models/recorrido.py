from sqlalchemy import Column, Integer, String, Numeric, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Recorrido(Base):
    __tablename__ = "recorrido"
    __table_args__ = {'schema': 'soderia'}

    id_recorrido = Column(Integer, primary_key=True, index=True)
    id_empleado = Column(Integer, ForeignKey("soderia.empleado.legajo"), nullable=False)
    id_reparto_dia = Column(Integer, ForeignKey("soderia.reparto_dia.id_reparto_dia"), nullable=False)
    patente = Column(String(10), ForeignKey("soderia.camion_reparto.patente"), nullable=False)
    dinero_inicial = Column(Numeric(12, 2), nullable=False, default=0.00)
    stock_inicial = Column(Integer, nullable=False, default=0)
    observacion = Column(Text)

    empleado = relationship("Empleado", back_populates="recorridos")
    reparto_dia = relationship("RepartoDia", back_populates="recorridos")
    camion_reparto = relationship("CamionReparto", back_populates="recorridos")
    movimientos_stock = relationship("MovimientoStock", back_populates="recorrido")
