"""Utilidades de seguridad: contrasenas, tokens JWT y API keys.

* Contrasenas de usuarios: hash con Argon2 (via ``pwdlib``).
* API keys de nodos IoT: hash SHA-256 determinista + comparacion en
  tiempo constante (``hmac.compare_digest``).
* Tokens de acceso/refresco: JWT firmados con HS256.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

import jwt
from pwdlib import PasswordHash

from app.core.config import obtener_configuracion

# Hasher Argon2 con parametros recomendados por la libreria.
_hasher = PasswordHash.recommended()


class TipoToken(str, Enum):
    """Tipos de token JWT emitidos por el backend."""

    ACCESO = "acceso"
    REFRESCO = "refresco"


# ---------------------------------------------------------------------
# Contrasenas
# ---------------------------------------------------------------------
def hashear_contrasena(contrasena: str) -> str:
    """Devuelve el hash Argon2 de una contrasena en texto plano."""
    return _hasher.hash(contrasena)


def verificar_contrasena(contrasena: str, hash_almacenado: str) -> bool:
    """Verifica una contrasena contra su hash Argon2."""
    try:
        return _hasher.verify(contrasena, hash_almacenado)
    except Exception:  # noqa: BLE001 - hash corrupto o formato invalido
        return False


# ---------------------------------------------------------------------
# API keys de nodos IoT
# ---------------------------------------------------------------------
def generar_api_key() -> str:
    """Genera una API key aleatoria y segura para un nodo IoT."""
    return secrets.token_urlsafe(32)


def hashear_api_key(api_key: str) -> str:
    """Devuelve el hash SHA-256 (hex) de una API key."""
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def verificar_api_key(api_key: str, hash_almacenado: str) -> bool:
    """Compara una API key con su hash en tiempo constante."""
    calculado = hashear_api_key(api_key)
    return hmac.compare_digest(calculado, hash_almacenado)


# ---------------------------------------------------------------------
# Tokens JWT
# ---------------------------------------------------------------------
def crear_token(
    sujeto: str,
    tipo: TipoToken = TipoToken.ACCESO,
    datos_extra: dict[str, Any] | None = None,
) -> str:
    """Crea un token JWT firmado.

    Args:
        sujeto: Identificador del sujeto (normalmente el id del usuario).
        tipo: Tipo de token (acceso o refresco).
        datos_extra: Claims adicionales a incluir.

    Returns:
        El token JWT codificado.
    """
    config = obtener_configuracion()
    ahora = datetime.now(tz=timezone.utc)
    if tipo is TipoToken.ACCESO:
        expiracion = ahora + timedelta(minutes=config.access_token_minutos)
    else:
        expiracion = ahora + timedelta(days=config.refresh_token_dias)

    carga: dict[str, Any] = {
        "sub": str(sujeto),
        "tipo": tipo.value,
        "iat": ahora,
        "exp": expiracion,
        "iss": config.app_nombre,
    }
    if datos_extra:
        carga.update(datos_extra)
    return jwt.encode(carga, config.jwt_secreto, algorithm=config.jwt_algoritmo)


def decodificar_token(token: str) -> dict[str, Any]:
    """Decodifica y valida un token JWT.

    Raises:
        jwt.ExpiredSignatureError: Si el token expiro.
        jwt.InvalidTokenError: Si el token es invalido.
    """
    config = obtener_configuracion()
    return jwt.decode(
        token,
        config.jwt_secreto,
        algorithms=[config.jwt_algoritmo],
        issuer=config.app_nombre,
    )
