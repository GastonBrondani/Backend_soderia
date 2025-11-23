# app/api/routers/auth.py
from __future__ import annotations
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, LoginResponse

router = APIRouter(prefix="/auth", tags=["Auth"])

# En la práctica estos valores deberían venir de tu .env
SECRET_KEY = "CAMBIA_ESTA_CLAVE_POR_ALGO_LARGO_Y_SECRETO"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 día, cambia a gusto


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    # 1) Buscar usuario por nombre_usuario
    user: Usuario | None = (
        db.query(Usuario)
        .filter(Usuario.nombre_usuario == payload.nombre_usuario.strip())
        .first()
    )
    if not user:
        # No revelamos si falló usuario o pass
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas.",
        )

    # 2) Verificar contraseña
    if not verify_password(payload.contrasena, user.contrasena):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas.",
        )

    # 3) Crear token (sin roles por ahora)
    token_data = {
        "sub": str(user.id_usuario),
        "nombre_usuario": user.nombre_usuario,
    }
    access_token = create_access_token(token_data)

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        id_usuario=user.id_usuario,
        nombre_usuario=user.nombre_usuario,
    )
