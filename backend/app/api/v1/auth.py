"""Endpoints de autenticacion del panel web."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.deps import SesionBd, UsuarioActual, validar_token_refresco
from app.core.excepciones import ErrorCredenciales
from app.core.seguridad import TipoToken, crear_token, verificar_contrasena
from app.schemas.auth import RespuestaToken, SolicitudRefresco
from app.schemas.usuario import UsuarioLeer
from app.services import usuarios as servicio_usuarios

router = APIRouter(prefix="/auth", tags=["Autenticacion"])


def _emitir_tokens(usuario_id: int, rol: str) -> RespuestaToken:
    extra = {"rol": rol}
    return RespuestaToken(
        access_token=crear_token(usuario_id, TipoToken.ACCESO, extra),
        refresh_token=crear_token(usuario_id, TipoToken.REFRESCO, extra),
        token_type="bearer",
    )


@router.post("/login", response_model=RespuestaToken, summary="Iniciar sesion")
def iniciar_sesion(
    base_datos: SesionBd,
    formulario: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> RespuestaToken:
    """Valida las credenciales (usuario/correo y contrasena) y emite tokens."""
    usuario = servicio_usuarios.obtener_por_correo(base_datos, formulario.username)
    if usuario is None or not verificar_contrasena(formulario.password, usuario.contrasena_hash):
        raise ErrorCredenciales("Correo o contrasena incorrectos.")
    if not usuario.activo:
        raise ErrorCredenciales("El usuario esta inactivo.")

    usuario.ultimo_acceso = datetime.now(tz=timezone.utc)
    base_datos.flush()

    rol = usuario.rol.nombre if usuario.rol else "operador"
    return _emitir_tokens(usuario.id, rol)


@router.post("/refresh", response_model=RespuestaToken, summary="Renovar el token de acceso")
def refrescar_token(base_datos: SesionBd, datos: SolicitudRefresco) -> RespuestaToken:
    """Emite un nuevo par de tokens a partir de un token de refresco valido."""
    usuario = validar_token_refresco(base_datos, datos.refresh_token)
    rol = usuario.rol.nombre if usuario.rol else "operador"
    return _emitir_tokens(usuario.id, rol)


@router.get("/me", response_model=UsuarioLeer, summary="Usuario autenticado actual")
def obtener_perfil(usuario: UsuarioActual) -> UsuarioLeer:
    """Devuelve el perfil del usuario asociado al token enviado."""
    return UsuarioLeer.model_validate(usuario)
