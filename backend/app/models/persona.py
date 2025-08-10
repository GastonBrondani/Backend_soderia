from sqlalchemy import Column, String
from database import Base

class Persona(Base):
    __tablename__ = "persona"
    __table_args__ = {'schema': 'soderia'}

    dni = Column(String(20), primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
