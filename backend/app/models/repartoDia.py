from sqlalchemy import Column, Integer, Numeric, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import date

class RepartoDia(Base):
    __tablename__ = "reparto_dia"
    __table_args__ = {'schema': 'soderia'}

    id_reparto_dia = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False, default=date.today)
    total_recaudado = Column(Numeric(12, 2), nullable=False, default=0.00)
    total_efectivo = Column(Numeric(12, 2), nullable=False, default=0.00)
    total_virtual = Column(Numeric(12, 2), nullable=False, default=0.00)
    observacion = Column(Text)
    id_usuario = Column(Integer, ForeignKey("soderia.usuario.id_usuario", ondelete="SET NULL"))
    id_empresa = Column(Integer, ForeignKey("soderia.empresa.id_empresa"))

    usuario = relationship("Usuario", back_populates="repartos")
    empresa = relationship("Empresa", back_populates="repartos")
