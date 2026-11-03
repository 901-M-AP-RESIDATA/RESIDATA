"""Endpoints de ingesta de imagenes desde los nodos IoT (ESP32-CAM).

La autenticacion de los nodos se realiza con la cabecera ``X-Api-Key``.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, File, UploadFile

from app.core.deps import ContenedorIoT, SesionBd
from app.core.excepciones import ErrorDatos
from app.core.logging import obtener_logger
from app.schemas.dispositivo import RespuestaClasificacion
from app.services import procesamiento

router = APIRouter(prefix="/dispositivo", tags=["Dispositivo IoT"])

logger = obtener_logger(__name__)

_EXTENSIONES_VALIDAS = {"jpg", "jpeg", "png", "webp"}


def _extension(filename: str | None) -> str:
    sufijo = Path(filename or "imagen.jpg").suffix.lower().lstrip(".")
    if sufijo not in _EXTENSIONES_VALIDAS:
        return "jpg"
    return sufijo


@router.post(
    "/clasificar",
    response_model=RespuestaClasificacion,
    summary="Clasificar una imagen enviada por un nodo",
)
def clasificar(
    base_datos: SesionBd,
    contenedor: ContenedorIoT,
    imagen: UploadFile = File(..., description="Imagen capturada por la camara"),
) -> RespuestaClasificacion:
    """Recibe una imagen, la clasifica y devuelve la categoria y el angulo del servo."""
    contenido = imagen.file.read()
    if not contenido:
        raise ErrorDatos("No se recibio ninguna imagen.")

    logger.info(
        "Ingesta recibida del contenedor %s (%s bytes).",
        contenedor.nombre,
        len(contenido),
    )
    return procesamiento.procesar_lectura(
        base_datos, contenedor, contenido, extension=_extension(imagen.filename)
    )
