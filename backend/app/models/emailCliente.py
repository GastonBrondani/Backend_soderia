from sqlalchemy import Column, Integer, String, Text, ForeignKey
from database import Base

class EmailCliente(Base):
    __tablename__ = "email_cliente"
    __table_args__ = {'schema': 'soderia'}

    id_email = Column(Integer, primary_key=True, index=True)
    legajo = Column(Integer, nullable=False)
    email = Column(String(100), nullable=False)
    estado = Column(String(20), nullable=False)
    observacion = Column(Text, nullable=True)

    # Si querés, podés agregar la FK así:
    # legajo = Column(Integer, ForeignKey("soderia.cliente.legajo"), nullable=False)
