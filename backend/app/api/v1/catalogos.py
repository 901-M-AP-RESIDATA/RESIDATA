"""Endpoints de catalogos: roles y categorias de residuo."""

from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import select

from app.core.deps import SesionBd, UsuarioActual
from app.db.modelos import CategoriaResiduo, Rol
from app.schemas.categoria import CategoriaResiduoLeer
from app.schemas.rol import RolLeer

router = APIRouter(tags=["Catalogos"])


@router.get("/roles", response_model=list[RolLeer], summary="Listar roles")
def listar_roles(base_datos: SesionBd, _usuario: UsuarioActual) -> list[RolLeer]:
    """Devuelve el catalogo de roles disponibles."""
    roles = base_datos.scalars(select(Rol).order_by(Rol.id)).all()
    return [RolLeer.model_validate(rol) for rol in roles]


@router.get(
    "/categorias",
    response_model=list[CategoriaResiduoLeer],
    summary="Listar categorias de residuo",
)
def listar_categorias(
    base_datos: SesionBd, _usuario: UsuarioActual
) -> list[CategoriaResiduoLeer]:
    """Devuelve las categorias de residuo (Organico, Inorganico, Peligroso)."""
    categorias = base_datos.scalars(
        select(CategoriaResiduo).order_by(CategoriaResiduo.id)
    ).all()
    return [CategoriaResiduoLeer.model_validate(categoria) for categoria in categorias]
