from sqlalchemy import Column, Integer, Text, ForeignKey, TIMESTAMP, func
from database import Base

class Historico(Base):
    __tablename__ = "historico"
    __table_args__ = {'schema': 'soderia'}

    id_historico = Column(Integer, primary_key=True, index=True)
    legajo = Column(Integer, nullable=False)
    id_evento = Column(Integer, nullable=False)
    fecha = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    observacion = Column(Text, nullable=True)
    id_pedido = Column(Integer, nullable=True)

    # Opcional, si querés poner las FK explícitas:
    # legajo = Column(Integer, ForeignKey("soderia.cliente.legajo"), nullable=False)
    # id_pedido = Column(Integer, ForeignKey("soderia.pedido.id_pedido", ondelete="SET NULL"), nullable=True)
    # id_evento = Column(Integer, ForeignKey("soderia.tipo_evento.id_evento"), nullable=False)
