"""Endpoints de gestion de usuarios (solo administradores)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.core.deps import SesionBd, UsuarioActual, requiere_admin
from app.db.modelos import Usuario
from app.schemas.comun import RespuestaPaginada, construir_paginada
from app.schemas.usuario import UsuarioActualizar, UsuarioCrear, UsuarioLeer
from app.services import usuarios as servicio_usuarios

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

AdminActual = Annotated[Usuario, Depends(requiere_admin)]


@router.get("", response_model=RespuestaPaginada[UsuarioLeer], summary="Listar usuarios")
def listar_usuarios(
    base_datos: SesionBd,
    _admin: AdminActual,
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=20, ge=1, le=1000),
) -> RespuestaPaginada[UsuarioLeer]:
    """Devuelve los usuarios del panel de forma paginada."""
    items, total = servicio_usuarios.listar(base_datos, pagina, limite)
    return construir_paginada(
        [UsuarioLeer.model_validate(item) for item in items], total, pagina, limite
    )


@router.post(
    "",
    response_model=UsuarioLeer,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario",
)
def crear_usuario(
    base_datos: SesionBd, _admin: AdminActual, datos: UsuarioCrear
) -> UsuarioLeer:
    """Crea un nuevo usuario del panel."""
    usuario = servicio_usuarios.crear(base_datos, datos)
    return UsuarioLeer.model_validate(usuario)


@router.get("/{usuario_id}", response_model=UsuarioLeer, summary="Obtener usuario")
def obtener_usuario(
    base_datos: SesionBd, _admin: AdminActual, usuario_id: int
) -> UsuarioLeer:
    """Devuelve un usuario por su identificador."""
    return UsuarioLeer.model_validate(servicio_usuarios.obtener(base_datos, usuario_id))


@router.patch("/{usuario_id}", response_model=UsuarioLeer, summary="Actualizar usuario")
def actualizar_usuario(
    base_datos: SesionBd,
    _admin: AdminActual,
    usuario_id: int,
    datos: UsuarioActualizar,
) -> UsuarioLeer:
    """Actualiza parcialmente un usuario."""
    return UsuarioLeer.model_validate(
        servicio_usuarios.actualizar(base_datos, usuario_id, datos)
    )


@router.delete(
    "/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar usuario"
)
def eliminar_usuario(
    base_datos: SesionBd, admin: AdminActual, usuario_id: int
) -> None:
    """Elimina un usuario (no permite eliminarse a si mismo)."""
    servicio_usuarios.eliminar(base_datos, usuario_id, admin)
