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

    # Envases entregados/devueltos en una visita SIN pedido.
    # Caso típico: el cliente no compra pero devuelve el envase.
    # `id_repartodia` es obligatorio si se mandan envases (de ahí se
    # resuelve la empresa para mover el stock).
    id_repartodia: Optional[int] = None
    envases: List[EnvaseMovimientoPedidoIn] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validar_envases(self):
        if self.envases and self.id_repartodia is None:
            raise ValueError(
                "id_repartodia es obligatorio cuando se registran envases."
            )
        return self

class VisitaOut(VisitaBase):
    model_config = ConfigDict(from_attributes=True)

    id_visita: int
    legajo: int
    idempotency_key: Optional[str] = None
    client_uuid: Optional[str] = None