"""Dependencias reutilizables de FastAPI: base de datos y seguridad.

Centraliza la autenticacion del panel web (JWT) y de los nodos IoT
(API key en cabecera ``X-Api-Key``).
"""

from __future__ import annotations

from typing import Annotated, Any

import jwt
from fastapi import Depends, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.excepciones import ErrorAutenticacion, ErrorPermiso
from app.core.seguridad import TipoToken, decodificar_token, hashear_api_key
from app.db.modelos import Contenedor, Usuario
from app.db.sesion import obtener_db

# Esquema OAuth2 (formulario usuario/contrasena) usado por /auth/login.
esquema_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

SesionBd = Annotated[Session, Depends(obtener_db)]


def _carga_desde_token(token: str, tipo_esperado: TipoToken) -> dict[str, Any]:
    """Valida un JWT y devuelve su carga (claims)."""
    try:
        carga = decodificar_token(token)
    except jwt.ExpiredSignatureError as exc:
        raise ErrorAutenticacion("La sesion expiro. Vuelve a iniciar sesion.") from exc
    except jwt.InvalidTokenError as exc:
        raise ErrorAutenticacion("Token invalido.") from exc

    if carga.get("tipo") != tipo_esperado.value:
        raise ErrorAutenticacion("Tipo de token incorrecto.")

    return carga


def obtener_usuario_actual(
    base_datos: SesionBd,
    token: Annotated[str | None, Depends(esquema_oauth2)],
) -> Usuario:
    """Dependencia que devuelve el usuario autenticado a partir del JWT."""
    if not token:
        raise ErrorAutenticacion("No se envio el token de acceso.")

    carga = _carga_desde_token(token, TipoToken.ACCESO)

    usuario = base_datos.get(Usuario, int(carga["sub"]))
    if usuario is None or not usuario.activo:
        raise ErrorAutenticacion("Usuario inexistente o inactivo.")
    return usuario


UsuarioActual = Annotated[Usuario, Depends(obtener_usuario_actual)]


def requiere_admin(usuario: UsuarioActual) -> Usuario:
    """Exige que el usuario autenticado tenga el rol ``administrador``."""
    if usuario.rol is None or usuario.rol.nombre != "administrador":
        raise ErrorPermiso("Se requiere el rol administrador para esta operacion.")
    return usuario


def validar_token_refresco(base_datos: Session, token: str) -> Usuario:
    """Valida un token de refresco y devuelve el usuario asociado."""
    carga = _carga_desde_token(token, TipoToken.REFRESCO)
    usuario = base_datos.get(Usuario, int(carga["sub"]))
    if usuario is None or not usuario.activo:
        raise ErrorAutenticacion("Usuario inexistente o inactivo.")
    return usuario


def contenedor_por_api_key(
    base_datos: SesionBd,
    api_key: Annotated[str | None, Header(alias="X-Api-Key")] = None,
) -> Contenedor:
    """Autentica un nodo IoT mediante su API key (cabecera ``X-Api-Key``)."""
    if not api_key:
        raise ErrorAutenticacion("Falta la cabecera X-Api-Key.")

    contenedor = base_datos.scalar(
        select(Contenedor).where(Contenedor.api_key_hash == hashear_api_key(api_key))
    )
    if contenedor is None:
        raise ErrorAutenticacion("API key invalida.")
    if contenedor.estado == "inactivo":
        raise ErrorPermiso("El contenedor esta inactivo.")
    return contenedor


ContenedorIoT = Annotated[Contenedor, Depends(contenedor_por_api_key)]
