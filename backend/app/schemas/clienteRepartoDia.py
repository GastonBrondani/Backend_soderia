from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator


# --- Catálogos sugeridos (podés ampliar si hace falta) ---
ESTADOS_PERMITIDOS = {
    "pendiente",
    "entregado",
    "ausente",
    "rechazado",
    "reprogramado",
    "parcial",
}

TURNOS_PERMITIDOS = {
    "mañana",
    "tarde",
    "noche",
}


# --------- CREATE (Planificación) ----------
class ClienteRepartoDiaCreate(BaseModel):
    """
    Crear la asignación de un cliente a un reparto del día (planificación).
    El id_repartodia vendrá en la ruta; acá sólo se pasa el cliente y datos de agenda.
    """
    legajo: int
    turno_de_la_visita: Optional[str] = None
    observacion: Optional[str] = None

    @field_validator("turno_de_la_visita")
    @classmethod
    def validar_turno(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v_norm = v.strip().lower()
        if v_norm and v_norm not in TURNOS_PERMITIDOS:
            raise ValueError(f"turno_de_la_visita inválido. Opciones: {sorted(TURNOS_PERMITIDOS)}")
        return v_norm or None

    @field_validator("observacion")
    @classmethod
    def trim_obs(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        return v or None


# --- Bulk para planificar varios clientes de una (opcional pero útil) ---
class PlanItem(BaseModel):
    legajo: int
    turno_de_la_visita: Optional[str] = None
    observacion: Optional[str] = None

    @field_validator("turno_de_la_visita")
    @classmethod
    def validar_turno(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v_norm = v.strip().lower()
        if v_norm and v_norm not in TURNOS_PERMITIDOS:
            raise ValueError(f"turno_de_la_visita inválido. Opciones: {sorted(TURNOS_PERMITIDOS)}")
        return v_norm or None

    @field_validator("observacion")
    @classmethod
    def trim_obs(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        return v or None


class PlanificarClientesIn(BaseModel):
    items: List[PlanItem]


# --------- UPDATE (Resultado de la visita) ----------
class ClienteRepartoDiaUpdate(BaseModel):
    """
    Patch de resultado. Todos opcionales: se actualiza sólo lo presente.
    """
    estado_de_la_visita: Optional[str] = None
    bidones_entregado: Optional[int] = None
    monto_abonado: Optional[Decimal] = None
    observacion: Optional[str] = None
    turno_de_la_visita: Optional[str] = None

    @field_validator("estado_de_la_visita")
    @classmethod
    def validar_estado(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v_norm = v.strip().lower()
        if v_norm and v_norm not in ESTADOS_PERMITIDOS:
            raise ValueError(f"estado_de_la_visita inválido. Opciones: {sorted(ESTADOS_PERMITIDOS)}")
        return v_norm or None

    @field_validator("turno_de_la_visita")
    @classmethod
    def validar_turno(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v_norm = v.strip().lower()
        if v_norm and v_norm not in TURNOS_PERMITIDOS:
            raise ValueError(f"turno_de_la_visita inválido. Opciones: {sorted(TURNOS_PERMITIDOS)}")
        return v_norm or None

    @field_validator("bidones_entregado")
    @classmethod
    def validar_bidones(cls, v: Optional[int]) -> Optional[int]:
        if v is None:
            return v
        if v < 0:
            raise ValueError("bidones_entregado no puede ser negativo.")
        return v

    @field_validator("monto_abonado")
    @classmethod
    def validar_monto(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is None:
            return v
        if v < 0:
            raise ValueError("monto_abonado no puede ser negativo.")
        # Normalizar a 2 decimales
        return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @field_validator("observacion")
    @classmethod
    def trim_obs(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        return v or None


# --------- OUT (Respuesta) ----------
class ClienteRepartoDiaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_repartodia: int
    legajo: int
    bidones_entregado: int
    monto_abonado: Decimal
    estado_de_la_visita: Optional[str] = None
    turno_de_la_visita: Optional[str] = None
    observacion: Optional[str] = None