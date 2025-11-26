from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field
from app.schemas.tipoEvento import TipoEventoOut


class HistoricoOut(BaseModel):
    """
    Para listar el historial de un cliente.
    """
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    id_historico: int
    legajo: int
    fecha: datetime
    observacion: Optional[str] = None
    datos: Optional[Dict[str, Any]] = None

    # En el modelo SQLAlchemy la relación seguramente se llama "tipo_evento",
    # pero en el JSON la exponemos como "evento".
    evento: TipoEventoOut = Field(alias="tipo_evento")
