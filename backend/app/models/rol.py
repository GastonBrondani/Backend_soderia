from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from database import Base

class Rol(Base):
    __tablename__ = "rol"
    __table_args__ = {'schema': 'soderia'}

    id_rol = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    descripcion = Column(Text)

    usuarios_roles = relationship("UsuarioRol", back_populates="rol")
