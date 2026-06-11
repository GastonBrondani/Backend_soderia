from datetime import datetime
from typing import Optional,Literal,List
from pydantic import BaseModel,ConfigDict,Field,model_validator

from app.schemas.envaseCliente import EnvaseMovimientoPedidoIn



class VisitaBase(BaseModel):
    fecha: Optional[datetime] = None
    estado: Literal[
        "cliente_compra",
        "cliente_no_compra",
        "postergacion_cliente",
    ]

class VisitaCreate(VisitaBase):
    # Offline sync: idempotencia. La tablet manda estos valores al reintentar.
    idempotency_key: Optional[str] = None
    client_uuid: Optional[str] = None

class VisitaOut(VisitaBase):
    model_config = ConfigDict(from_attributes=True)

    id_visita: int
    legajo: int
    idempotency_key: Optional[str] = None
    client_uuid: Optional[str] = None