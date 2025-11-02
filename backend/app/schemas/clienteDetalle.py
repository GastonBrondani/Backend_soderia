from typing import Optional, List
from pydantic import BaseModel,ConfigDict,Field

#schemas para mostrar detalles relacionados
from app.schemas.persona import PersonaOut
from app.schemas.direccionCliente import DireccionClienteOut
from app.schemas.telefonoCliente import TelefonoClienteOut
from app.schemas.emailCliente import MailClienteOut
#from app.schemas.documentos import DocumentosOut
from app.schemas.producto import ProductoOut
from app.schemas.clienteCuenta import ClienteCuentaOut



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