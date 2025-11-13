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
from app.schemas.clienteDiaSemana import ClienteDiaSemanaOut




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




# relaciones adicionales

# app/schemas/clienteDetalle.py
from typing import List, Optional
from pydantic import Field
from app.schemas.cliente import ClienteOut
from app.schemas.direccionCliente import DireccionClienteOut
from app.schemas.telefonoCliente import TelefonoClienteOut
from app.schemas.emailCliente import MailClienteOut
from app.schemas.producto import ProductoOut
from app.schemas.clienteCuenta import ClienteCuentaOut
from app.schemas.pedido import PedidoOutCorto
from app.schemas.historico import HistoricoOut
from app.schemas.cliente import DiaSemanaEnum, TurnoVisitaEnum

class ClienteDetalleOut(ClienteOut):
    direcciones: List[DireccionClienteOut] = Field(default_factory=list)
    telefonos: List[TelefonoClienteOut] = Field(default_factory=list)
    emails: List[MailClienteOut] = Field(default_factory=list)
    productos: List[ProductoOut] = Field(default_factory=list)
    cuentas: List[ClienteCuentaOut] = Field(default_factory=list)

    pedidos: List[PedidoOutCorto] = Field(default_factory=list)
    historicos: List[HistoricoOut] = Field(default_factory=list)

    dias_visita: List[DiaSemanaEnum] = Field(default_factory=list)
    turno_visita: Optional[TurnoVisitaEnum] = None

