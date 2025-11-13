# app/schemas/historico.py
# EMMA
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class HistoricoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_historico: int
    fecha: datetime
    evento: Optional[str] = None   # o podés hacer un subobjeto si querés
    observacion: Optional[str] = None
