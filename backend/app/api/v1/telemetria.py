"""Endpoints para consultar telemetria no estructurada almacenada en MongoDB."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from app.core.deps import UsuarioActual
from app.db.mongo import listar_telemetria_iot

router = APIRouter(prefix="/telemetria", tags=["Telemetría IoT (MongoDB)"])


@router.get("", summary="Listar telemetría de MongoDB")
def listar_telemetria(
    _usuario: UsuarioActual,
    limite: int = Query(default=20, ge=1, le=100),
) -> dict[str, Any]:
    """Devuelve los ultimos documentos crudos de telemetria IoT guardados en MongoDB."""
    documentos = listar_telemetria_iot(limite)
    return {
        "motor": "MongoDB NoSQL",
        "coleccion": "telemetria_iot",
        "total_documentos": len(documentos),
        "documentos": documentos,
    }
