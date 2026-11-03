"""Excepciones de dominio y manejadores de error centralizados.

Todas las respuestas de error del API comparten un mismo formato JSON::

    {"error": {"codigo": "no_encontrado", "mensaje": "..."}}
"""

from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import obtener_logger

logger = obtener_logger(__name__)


# ---------------------------------------------------------------------
# Excepciones de dominio
# ---------------------------------------------------------------------
class ErrorResiData(Exception):
    """Excepcion base de dominio del backend ResiData."""

    codigo = "error_interno"
    estado = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, mensaje: str) -> None:
        self.mensaje = mensaje
        super().__init__(mensaje)


class ErrorNoEncontrado(ErrorResiData):
    """Recurso solicitado inexistente (HTTP 404)."""

    codigo = "no_encontrado"
    estado = status.HTTP_404_NOT_FOUND


class ErrorCredenciales(ErrorResiData):
    """Credenciales invalidas (HTTP 401)."""

    codigo = "credenciales_invalidas"
    estado = status.HTTP_401_UNAUTHORIZED


class ErrorAutenticacion(ErrorResiData):
    """Falta autenticacion o el token es invalido (HTTP 401)."""

    codigo = "no_autenticado"
    estado = status.HTTP_401_UNAUTHORIZED


class ErrorPermiso(ErrorResiData):
    """El usuario no tiene permisos suficientes (HTTP 403)."""

    codigo = "permiso_denegado"
    estado = status.HTTP_403_FORBIDDEN


class ErrorDatos(ErrorResiData):
    """Datos de entrada invalidos (HTTP 400)."""

    codigo = "datos_invalidos"
    estado = status.HTTP_400_BAD_REQUEST


class ErrorConflicto(ErrorResiData):
    """Conflicto con el estado actual (HTTP 409)."""

    codigo = "conflicto"
    estado = status.HTTP_409_CONFLICT


class ErrorLimite(ErrorResiData):
    """Se supero un limite (por ejemplo, tamano de archivo, HTTP 413)."""

    codigo = "limite_excedido"
    estado = 413


def _respuesta_error(codigo: str, mensaje: str, estado: int) -> JSONResponse:
    return JSONResponse(
        status_code=estado,
        content={"error": {"codigo": codigo, "mensaje": mensaje}},
    )


# ---------------------------------------------------------------------
# Registro de manejadores
# ---------------------------------------------------------------------
def registrar_manejadores(app: FastAPI) -> None:
    """Registra los manejadores de error globales en la app."""

    @app.exception_handler(ErrorResiData)
    async def _manejar_dominio(_: Request, exc: ErrorResiData) -> JSONResponse:
        return _respuesta_error(exc.codigo, exc.mensaje, exc.estado)

    @app.exception_handler(RequestValidationError)
    async def _manejar_validacion(_: Request, exc: RequestValidationError) -> JSONResponse:
        return _respuesta_error("datos_invalidos", "Datos de entrada invalidos.", 422)

    @app.exception_handler(StarletteHTTPException)
    async def _manejar_http(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        return _respuesta_error("http_error", str(exc.detail), exc.status_code)

    @app.exception_handler(Exception)
    async def _manejar_inesperado(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Error no controlado: %s", exc)
        return _respuesta_error(
            "error_interno", "Error interno del servidor.", status.HTTP_500_INTERNAL_SERVER_ERROR
        )
