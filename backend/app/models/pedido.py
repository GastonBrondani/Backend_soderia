from sqlalchemy import Column, Integer, String, Numeric, Text, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from database import Base

class Pedido(Base):
    __tablename__ = "pedido"
    __table_args__ = {'schema': 'soderia'}

    id_pedido = Column(Integer, primary_key=True, index=True)
    legajo = Column(Integer, ForeignKey("soderia.cliente.legajo"), nullable=False)
    fecha = Column(TIMESTAMP, nullable=False, server_default=func.now())
    monto_total = Column(Numeric(12, 2), nullable=False)
    monto_abonado = Column(Numeric(12, 2), nullable=False, default=0.00)
    estado = Column(String(30), nullable=False)
    observacion = Column(Text, nullable=True)
    id_medio_pago = Column(Integer, ForeignKey("soderia.medio_pago.id_medio_pago"), nullable=True)
    id_empresa = Column(Integer, ForeignKey("soderia.empresa.id_empresa"), nullable=True)
    id_reparto_dia = Column(Integer, ForeignKey("soderia.reparto_dia.id_reparto_dia"), nullable=True)
