from pydantic import BaseModel, ConfigDict
from typing import Optional

from app.schemas.enums_cliente import DiaSemanaEnum, TurnoVisitaEnum, PosicionEnum


class ClienteDiaSemanaBase(BaseModel):
    id_cliente: int  # lo podés ignorar en create si el servidor ya conoce el legajo
    id_dia: int
    turno_visita: Optional[str] = None


class ClienteDiaSemanaCreate(ClienteDiaSemanaBase):
    posicion: PosicionEnum = PosicionEnum.final
    despues_de_legajo: Optional[int] = None  # requerido si posicion = "despues"


class ClienteDiaSemanaUpdate(BaseModel):
    turno_visita: Optional[str] = None
    posicion: Optional[PosicionEnum] = None
    despues_de_legajo: Optional[int] = None


class ClienteDiaSemanaOut(ClienteDiaSemanaBase):
    model_config = ConfigDict(from_attributes=True)
    orden: Optional[int] = None


class FrecuenciaItemIn(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    dia: DiaSemanaEnum  # "lun".."dom"
    turno: Optional[TurnoVisitaEnum]  # "manana"|"tarde"|"noche"|None
    posicion: PosicionEnum = PosicionEnum.final
    despues_de_legajo: Optional[int] = None  # requerido si posicion="despues"
    

class ClienteDiaVisitaOut(BaseModel):
    id_dia: int
    nombre_dia: str
    turno_visita: Optional[str] = None
