"""Gestor de conexiones WebSocket para notificaciones en tiempo real."""

from __future__ import annotations

import asyncio
import threading
from typing import Any

from fastapi import WebSocket

from app.core.logging import obtener_logger

logger = obtener_logger(__name__)


class GestorConexiones:
    """Administra los clientes WebSocket conectados y les difunde eventos.

    El backend ejecuta los endpoints de ingesta en un hilo del pool de
    FastAPI, por lo que :meth:`difundir` programa la emision en el bucle de
    eventos donde viven los WebSocket.
    """

    def __init__(self) -> None:
        self._conexiones: set[WebSocket] = set()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._candado = threading.Lock()

    async def conectar(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._loop = asyncio.get_running_loop()
        with self._candado:
            self._conexiones.add(websocket)
        logger.info("WebSocket conectado (%d activos).", len(self._conexiones))

    def desconectar(self, websocket: WebSocket) -> None:
        with self._candado:
            self._conexiones.discard(websocket)
        logger.info("WebSocket desconectado (%d activos).", len(self._conexiones))

    @property
    def activos(self) -> int:
        return len(self._conexiones)

    async def _enviar(self, evento: dict[str, Any]) -> None:
        with self._candado:
            conexiones = list(self._conexiones)
        for websocket in conexiones:
            try:
                await websocket.send_json(evento)
            except Exception:  # noqa: BLE001 - conexion caida
                self.desconectar(websocket)

    def difundir(self, evento: dict[str, Any]) -> None:
        """Difunde un evento a todos los clientes (seguro entre hilos)."""
        loop = self._loop
        if loop is None or loop.is_closed():
            return
        try:
            asyncio.run_coroutine_threadsafe(self._enviar(evento), loop)
        except RuntimeError:  # pragma: no cover - bucle detenido
            logger.debug("No se pudo difundir el evento: el bucle esta detenido.")


# Instancia unica compartida por toda la aplicacion.
gestor = GestorConexiones()
