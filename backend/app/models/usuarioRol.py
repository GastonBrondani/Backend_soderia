from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class UsuarioRol(Base):
    __tablename__ = "usuario_rol"
    __table_args__ = {'schema': 'soderia'}

    id_rol = Column(Integer, ForeignKey("soderia.rol.id_rol"), primary_key=True)
    id_usuario = Column(Integer, ForeignKey("soderia.usuario.id_usuario"), primary_key=True)

    rol = relationship("Rol", back_populates="usuarios_roles")
    usuario = relationship("Usuario", back_populates="roles")
