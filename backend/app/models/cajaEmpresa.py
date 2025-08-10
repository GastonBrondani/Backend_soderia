from sqlalchemy import Column, Integer, String, Numeric, Text, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class CajaEmpresa(Base):
    __tablename__ = "caja_empresa"
    __table_args__ = (
        {'schema': 'soderia'},
        CheckConstraint("tipo IN ('INGRESO', 'EGRESO')", name="caja_empresa_tipo_check"),
    )

    id_caja_empresa = Column(Integer, primary_key=True, index=True)
    id_empresa = Column(Integer, ForeignKey("soderia.empresa.id_empresa"), nullable=False)
    id_tipo_movimiento = Column(Integer, ForeignKey("soderia.tipo_movimiento_caja.id_tipo_movimiento"), nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow, nullable=False)
    tipo = Column(String(10), nullable=False)
    monto = Column(Numeric(12,2), nullable=False)
    observacion = Column(Text)
    id_medio_pago = Column(Integer, ForeignKey("soderia.medio_pago.id_medio_pago"))

    empresa = relationship("Empresa", back_populates="caja_empresas")
    tipo_movimiento = relationship("TipoMovimientoCaja", back_populates="caja_empresas")
    medio_pago = relationship("MedioPago", back_populates="caja_empresas")
