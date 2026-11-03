"""Canal WebSocket para notificaciones en tiempo real.

El cliente se conecta a ``/api/v1/ws?token=<access_token>`` y recibe eventos
``nueva_clasificacion`` y ``alerta_peligroso``.
"""

from __future__ import annotations

import jwt
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.core.logging import obtener_logger
from app.core.seguridad import TipoToken, decodificar_token
from app.db.modelos import Usuario
from app.db.sesion import FabricaSesiones
from app.services.tiempo_real import gestor

router = APIRouter(tags=["Tiempo real"])

logger = obtener_logger(__name__)


def _usuario_valido(token: str | None) -> bool:
    if not token:
        return False
    try:
        carga = decodificar_token(token)
    except jwt.InvalidTokenError:
        return False
    if carga.get("tipo") != TipoToken.ACCESO.value:
        return False
    with FabricaSesiones() as sesion:
        usuario = sesion.get(Usuario, int(carga["sub"]))
        return usuario is not None and usuario.activo


@router.websocket("/ws")
async def tiempo_real(websocket: WebSocket, token: str | None = Query(default=None)) -> None:
    """Acepta la conexion, valida el token y mantiene el canal abierto."""
    if not _usuario_valido(token):
        await websocket.close(code=1008)
        return

    await gestor.conectar(websocket)
    try:
        while True:
            # El cliente normalmente no envia datos: recibir sirve para
            # detectar la desconexion y descartar mensajes entrantes.
            await websocket.receive_text()
    except WebSocketDisconnect:
        gestor.desconectar(websocket)
    except Exception:  # noqa: BLE001 - cierre abrupto
        gestor.desconectar(websocket)
        logger.debug("WebSocket cerrado de forma inesperada.")
