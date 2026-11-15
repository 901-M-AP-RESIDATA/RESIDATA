"""Endpoint de salud del servicio."""

from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import obtener_configuracion
from app.db.mongo import verificar_conexion_mongo
from app.db.sesion import FabricaSesiones

router = APIRouter(tags=["Salud"])


@router.get("/health", summary="Estado del servicio")
def salud() -> dict[str, object]:
    """Devuelve el estado del backend y de las conexiones a PostgreSQL y MongoDB."""
    config = obtener_configuracion()
    base_sql_ok = True
    try:
        with FabricaSesiones() as sesion:
            sesion.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001
        base_sql_ok = False

    base_mongo_ok = verificar_conexion_mongo()

    return {
        "estado": "ok" if (base_sql_ok and base_mongo_ok) else "degradado",
        "aplicacion": config.app_nombre,
        "version": config.app_version,
        "entorno": config.entorno,
        "base_datos_sql": "conectada" if base_sql_ok else "sin_conexion",
        "base_datos_nosql": "conectada" if base_mongo_ok else "sin_conexion",
    }
