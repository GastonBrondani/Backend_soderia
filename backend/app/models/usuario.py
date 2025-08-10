from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class Usuario(Base):
    __tablename__ = "usuario"
    __table_args__ = {'schema': 'soderia'}

    id_usuario = Column(Integer, primary_key=True, index=True)
    legajo = Column(Integer, ForeignKey("soderia.cliente.legajo"), nullable=False)  # FK a cliente(legajo)
    nombre_usuario = Column(String(50), nullable=False, unique=False)
    contraseña = Column(String(100), nullable=False)
    dni = Column(String(20), ForeignKey("soderia.persona.dni"), nullable=True, unique=True)

