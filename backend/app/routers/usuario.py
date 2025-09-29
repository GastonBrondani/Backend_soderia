from __future__ import annotations
import hashlib, secrets
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioOut

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

def _hash_password(raw: str) -> str:
    """PBKDF2-SHA256 (stdlib). Formato: pbkdf2_sha256$iter$salt$hex"""
    salt = secrets.token_hex(16)
    iterations = 100_000
    dk = hashlib.pbkdf2_hmac("sha256", raw.encode("utf-8"), salt.encode("utf-8"), iterations)
    return f"pbkdf2_sha256$${iterations}$${salt}$${dk.hex()}".replace("$$", "$")

@router.post("/", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def crear_usuario(payload: UsuarioCreate, db: Session = Depends(get_db)):
    hashed = _hash_password(payload.contrasena)  # alias "contraseña" -> .contrasena
    entity = Usuario(
        nombre_usuario=payload.nombre_usuario,
        contrasena=hashed,  # tu modelo debe mapear a la columna "contraseña"
        legajo_empleado=payload.legajo_empleado,
        legajo_cliente=payload.legajo_cliente,
    )
    try:
        db.add(entity)
        db.commit()
        db.refresh(entity)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No se pudo crear el usuario (duplicado o FK inválida).",
        ) from e
    return entity
