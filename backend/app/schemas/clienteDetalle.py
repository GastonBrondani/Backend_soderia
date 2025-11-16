from typing import Optional, List
from pydantic import BaseModel,ConfigDict,Field

#schemas para mostrar detalles relacionados
from app.schemas.persona import PersonaOut,PersonaUpdate
from app.schemas.direccionCliente import DireccionClienteOut, DireccionClienteUpdate
from app.schemas.telefonoCliente import TelefonoClienteOut, TelefonoClienteUpdate
from app.schemas.emailCliente import MailClienteOut, MailClienteUpdate
#from app.schemas.documentos import DocumentosOut
from app.schemas.producto import ProductoOut
from app.schemas.clienteCuenta import ClienteCuentaOut, ClienteCuentaUpdate
from app.schemas.clienteDiaSemana import ClienteDiaSemanaOut, ClienteDiaSemanaUpdate



#Mostramos todo lo relacionado al cliente.
class ClienteDetalleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    legajo: int
    persona: Optional[PersonaOut] = None
    direcciones: List[DireccionClienteOut] = Field(default_factory=list)
    telefonos: List[TelefonoClienteOut] = Field(default_factory=list)
    emails: List[MailClienteOut] = Field(default_factory=list)
    #documentos: List[DocumentosOut] = Field(default_factory=list)
    productos: List[ProductoOut] = Field(default_factory=list)
    cuentas: List[ClienteCuentaOut] = Field(default_factory=list)
    dias_semanas: List[ClienteDiaSemanaOut] = Field(default_factory=list)

#Esquema para actualizar todo lo relacionado al cliente.
#Ir agregando si es necesario.
class ClienteDetalleUpdate(BaseModel):
    persona: Optional[PersonaUpdate] = None
    direcciones: List[DireccionClienteUpdate] = None
    telefonos: List[TelefonoClienteUpdate] = None
    emails: List[MailClienteUpdate] = None
    cuentas: List[ClienteCuentaUpdate] = None
    dias_semanas: List[ClienteDiaSemanaUpdate] = None