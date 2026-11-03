"""Agregador de routers del API v1.

Registra todos los routers de la version 1: salud, autenticacion, usuarios,
catalogos, contenedores, ingesta IoT, historico, alertas, dashboard y
WebSocket de tiempo real.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import (
    alertas,
    auth,
    catalogos,
    contenedores,
    dashboard,
    dispositivo,
    historico,
    salud,
    usuarios,
    ws,
)

api_router = APIRouter()
api_router.include_router(salud.router)
api_router.include_router(auth.router)
api_router.include_router(catalogos.router)
api_router.include_router(usuarios.router)
api_router.include_router(contenedores.router)
api_router.include_router(dispositivo.router)
api_router.include_router(historico.router)
api_router.include_router(alertas.router)
api_router.include_router(dashboard.router)
api_router.include_router(ws.router)
