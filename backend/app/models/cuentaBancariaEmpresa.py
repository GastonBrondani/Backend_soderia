from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class CuentaBancariaEmpresa(Base):
    __tablename__ = "cuenta_bancaria_empresa"
    __table_args__ = {'schema': 'soderia'}

    id_cuenta = Column(Integer, primary_key=True, index=True)
    id_empresa = Column(Integer, ForeignKey("soderia.empresa.id_empresa"), nullable=False)
    titular_cuenta = Column(String(100), nullable=False)
    cbu = Column(String(22), nullable=False, unique=True)
    alias = Column(String(50), nullable=True)
    numero_de_cuenta = Column(String(20), nullable=False)
    tipo_cuenta = Column(String(30), nullable=False)  # Tipo puede ser CUENTA_CORRIENTE, CAJA_AHORRO, CUENTA_INVERSION
    banco = Column(String(50), nullable=False)
    activa = Column(Boolean, nullable=False, default=True)

    empresa = relationship("Empresa", back_populates="cuentas_bancarias")
