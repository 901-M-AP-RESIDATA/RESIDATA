"""Endpoint de salud del servicio."""

from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import obtener_configuracion
from app.db.sesion import FabricaSesiones

router = APIRouter(tags=["Salud"])


@router.get("/health", summary="Estado del servicio")
def salud() -> dict[str, object]:
    """Devuelve el estado del backend y de la conexion a la base de datos."""
    config = obtener_configuracion()
    base_ok = True
    try:
        with FabricaSesiones() as sesion:
            sesion.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001
        base_ok = False

    return {
        "estado": "ok" if base_ok else "degradado",
        "aplicacion": config.app_nombre,
        "version": config.app_version,
        "entorno": config.entorno,
        "base_datos": "conectada" if base_ok else "sin_conexion",
    }
