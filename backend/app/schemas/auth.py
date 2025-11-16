# app/schemas/auth.py
from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    nombre_usuario: str
    # Permitimos que en JSON venga como "contraseña"
    contrasena: str = Field(alias="contraseña", min_length=1)


class LoginResponse(BaseModel):
    # Por ahora, sin roles ni nada raro
    access_token: str
    token_type: str = "bearer"

    # Si querés también devolver info básica del usuario:
    id_usuario: int
    nombre_usuario: str
