from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from database import Base

class ClienteCuenta(Base):
    __tablename__ = "cliente_cuenta"
    __table_args__ = {'schema': 'soderia'}

    id_cuenta = Column(Integer, primary_key=True, index=True)
    legajo = Column(Integer, nullable=False)
    saldo = Column(Numeric(10, 2), nullable=False, default=0.00)
    deuda = Column(Numeric(10, 2), nullable=False, default=0.00)
    estado = Column(String(20), nullable=False)
    tipo_de_cuenta = Column(String(30), nullable=False)
    numero_bidones = Column(Integer, nullable=False, default=0)

    # Foreign key explícito opcional:
    # legajo = Column(Integer, ForeignKey("soderia.cliente.legajo"), nullable=False)
