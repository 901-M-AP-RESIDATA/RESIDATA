"""Endpoints de gestion de contenedores (nodos ESP32-CAM)."""

from __future__ import annotations

from fastapi import APIRouter, Query, status

from app.core.deps import SesionBd, UsuarioActual
from app.db.modelos import Contenedor
from app.schemas.comun import RespuestaPaginada, construir_paginada
from app.schemas.contenedor import (
    ContenedorActualizar,
    ContenedorConApiKey,
    ContenedorCrear,
    ContenedorLeer,
    EstadoContenedorDetalle,
)
from app.services import contenedores as servicio_contenedores

router = APIRouter(prefix="/contenedores", tags=["Contenedores"])


def _con_api_key(contenedor: Contenedor, api_key: str) -> ContenedorConApiKey:
    return ContenedorConApiKey(
        id=contenedor.id,
        nombre=contenedor.nombre,
        ubicacion=contenedor.ubicacion,
        estado=contenedor.estado,
        ultima_conexion=contenedor.ultima_conexion,
        fecha_creacion=contenedor.fecha_creacion,
        api_key=api_key,
    )


@router.get("", response_model=RespuestaPaginada[ContenedorLeer], summary="Listar contenedores")
def listar_contenedores(
    base_datos: SesionBd,
    _usuario: UsuarioActual,
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=20, ge=1, le=1000),
) -> RespuestaPaginada[ContenedorLeer]:
    """Devuelve los contenedores registrados de forma paginada."""
    items, total = servicio_contenedores.listar(base_datos, pagina, limite)
    return construir_paginada(
        [ContenedorLeer.model_validate(item) for item in items], total, pagina, limite
    )


@router.post(
    "",
    response_model=ContenedorConApiKey,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar contenedor",
)
def crear_contenedor(
    base_datos: SesionBd, _usuario: UsuarioActual, datos: ContenedorCrear
) -> ContenedorConApiKey:
    """Registra un contenedor y devuelve su API key (solo se muestra una vez)."""
    contenedor, api_key = servicio_contenedores.crear(base_datos, datos)
    return _con_api_key(contenedor, api_key)


@router.get(
    "/{contenedor_id}",
    response_model=EstadoContenedorDetalle,
    summary="Detalle de contenedor",
)
def obtener_contenedor(
    base_datos: SesionBd, _usuario: UsuarioActual, contenedor_id: int
) -> EstadoContenedorDetalle:
    """Devuelve el detalle ampliado de un contenedor (actividad y ultima categoria)."""
    return servicio_contenedores.obtener_detalle(base_datos, contenedor_id)


@router.patch(
    "/{contenedor_id}", response_model=ContenedorLeer, summary="Actualizar contenedor"
)
def actualizar_contenedor(
    base_datos: SesionBd,
    _usuario: UsuarioActual,
    contenedor_id: int,
    datos: ContenedorActualizar,
) -> ContenedorLeer:
    """Actualiza parcialmente un contenedor."""
    contenedor = servicio_contenedores.actualizar(base_datos, contenedor_id, datos)
    return ContenedorLeer.model_validate(contenedor)


@router.delete(
    "/{contenedor_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar contenedor"
)
def eliminar_contenedor(
    base_datos: SesionBd, _usuario: UsuarioActual, contenedor_id: int
) -> None:
    """Elimina un contenedor."""
    servicio_contenedores.eliminar(base_datos, contenedor_id)


@router.post(
    "/{contenedor_id}/regenerar-clave",
    response_model=ContenedorConApiKey,
    summary="Regenerar API key",
)
def regenerar_clave(
    base_datos: SesionBd, _usuario: UsuarioActual, contenedor_id: int
) -> ContenedorConApiKey:
    """Genera una nueva API key para el contenedor (invalida la anterior)."""
    contenedor, api_key = servicio_contenedores.regenerar_clave(base_datos, contenedor_id)
    return _con_api_key(contenedor, api_key)
