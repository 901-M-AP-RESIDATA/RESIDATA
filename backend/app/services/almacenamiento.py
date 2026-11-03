"""Servicio de almacenamiento de imagenes enviadas por los nodos IoT."""

from __future__ import annotations

import secrets
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import obtener_configuracion
from app.core.excepciones import ErrorDatos, ErrorLimite
from app.core.logging import obtener_logger

logger = obtener_logger(__name__)


def validar_tamano(imagen: bytes) -> None:
    """Comprueba que la imagen no supere el tamano maximo permitido."""
    config = obtener_configuracion()
    if not imagen:
        raise ErrorDatos("La imagen esta vacia.")
    if len(imagen) > config.tamano_max_imagen_bytes:
        raise ErrorLimite(
            f"La imagen supera el maximo de {config.tamano_max_imagen_mb} MB."
        )


def guardar_imagen(imagen: bytes, extension: str = "jpg") -> str:
    """Guarda la imagen en disco y devuelve su ruta relativa.

    Las imagenes se organizan por fecha: ``<directorio>/clasificaciones/
    AAAA-MM-DD/clasif_<marca>_<aleatorio>.<ext>``.
    """
    validar_tamano(imagen)
    config = obtener_configuracion()

    base = Path(config.directorio_almacenamiento)
    hoy = datetime.now(tz=timezone.utc)
    subcarpeta = base / "clasificaciones" / hoy.strftime("%Y-%m-%d")
    subcarpeta.mkdir(parents=True, exist_ok=True)

    marca = hoy.strftime("%Y%m%d%H%M%S")
    nombre = f"clasif_{marca}_{secrets.token_hex(4)}.{extension}"
    destino = subcarpeta / nombre

    try:
        destino.write_bytes(imagen)
    except OSError as exc:  # pragma: no cover - dependiente del sistema
        logger.exception("No se pudo guardar la imagen en %s", destino)
        raise ErrorDatos("No se pudo almacenar la imagen.") from exc

    logger.info("Imagen guardada en %s", destino)
    return destino.as_posix()
