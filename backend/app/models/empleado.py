from sqlalchemy import Column, Integer, String, Date, ForeignKey
from database import Base

class Empleado(Base):
    __tablename__ = "empleado"
    __table_args__ = {'schema': 'soderia'}

    legajo = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, nullable=False)
    fecha_ingreso = Column(Date, nullable=False)
    dni = Column(String, nullable=False)

    # Las FK quedan reflejadas con ForeignKey si querés, por ejemplo:
    # dni = Column(String, ForeignKey("soderia.persona.dni"), nullable=False)
