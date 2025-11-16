# app/core/security.py
from __future__ import annotations
import hashlib
import hmac
import secrets


ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 100_000


def hash_password(raw: str) -> str:
    """
    Genera un hash PBKDF2-SHA256.
    Formato: pbkdf2_sha256$iteraciones$salt$hashhex
    """
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        raw.encode("utf-8"),
        salt.encode("utf-8"),
        ITERATIONS,
    )
    return f"{ALGORITHM}${ITERATIONS}${salt}${dk.hex()}"


def verify_password(raw: str, hashed: str) -> bool:
    """
    Verifica una contraseña en texto plano contra un hash PBKDF2.
    """
    try:
        algorithm, iterations_str, salt, hash_hex = hashed.split("$", 3)
    except ValueError:
        return False

    if algorithm != ALGORITHM:
        return False

    try:
        iterations = int(iterations_str)
    except ValueError:
        return False

    new_dk = hashlib.pbkdf2_hmac(
        "sha256",
        raw.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    )
    return hmac.compare_digest(new_dk.hex(), hash_hex)
