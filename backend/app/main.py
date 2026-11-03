"""Punto de entrada de la aplicacion FastAPI de ResiData.

Ejecucion en desarrollo (desde la carpeta ``backend``)::

    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Documentacion interactiva: http://localhost:8000/docs
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import obtener_configuracion
from app.core.excepciones import registrar_manejadores
from app.core.logging import configurar_logging, obtener_logger
from app.db.sesion import motor

config = obtener_configuracion()
logger = obtener_logger(__name__)


@asynccontextmanager
async def ciclo_vida(app: FastAPI):
    """Gestiona los recursos que se inicializan y liberan con la app."""
    configurar_logging()
    logger.info("Iniciando %s v%s (entorno=%s)", config.app_nombre, config.app_version, config.entorno)
    try:
        yield
    finally:
        motor.dispose()
        logger.info("Aplicacion detenida y conexiones liberadas.")


def crear_app() -> FastAPI:
    """Crea y configura la instancia de FastAPI."""
    app = FastAPI(
        title=config.app_nombre,
        version=config.app_version,
        description=(
            "API REST del sistema IoT/IA de clasificacion de residuos ResiData. "
            "Nodos ESP32-CAM envian imagenes, la IA clasifica y el backend "
            "persiste historicos, genera alertas y notifica por WebSocket."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=ciclo_vida,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.origenes_cors,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    registrar_manejadores(app)
    app.include_router(api_router, prefix="/api/v1")

    @app.get("/", include_in_schema=False)
    def raiz() -> dict[str, str]:
        """Redirige informativamente a la documentacion del API."""
        return {"mensaje": f"{config.app_nombre} v{config.app_version}", "docs": "/docs"}

    return app


app = crear_app()
