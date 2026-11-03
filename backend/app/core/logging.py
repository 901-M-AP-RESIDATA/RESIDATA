"""Configuracion de logging estructurado.

Soporta dos formatos: ``consola`` (legible para desarrollo) y ``json``
(una linea JSON por evento, ideal para produccion y agregadores).
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

from app.core.config import obtener_configuracion

_RESERVED = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
    "taskName",
    "message",
}


class FormateadorJSON(logging.Formatter):
    """Formateador que serializa cada registro como una linea JSON."""

    def format(self, record: logging.LogRecord) -> str:
        registro: dict[str, Any] = {
            "fecha": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "nivel": record.levelname,
            "logger": record.name,
            "mensaje": record.getMessage(),
        }
        for clave, valor in record.__dict__.items():
            if clave not in _RESERVED:
                registro[clave] = valor
        if record.exc_info:
            registro["excepcion"] = self.formatException(record.exc_info)
        return json.dumps(registro, ensure_ascii=False, default=str)


def configurar_logging(nivel: str | None = None, formato: str | None = None) -> None:
    """Configura el logging raiz una sola vez.

    Args:
        nivel: Nivel de log (por ejemplo ``INFO``). Si es ``None`` se toma
            de la configuracion.
        formato: ``consola`` o ``json``. Si es ``None`` se toma de la
            configuracion.
    """
    config = obtener_configuracion()
    nivel_efectivo = (nivel or config.log_nivel).upper()
    formato_efectivo = formato or config.log_formato

    manejador = logging.StreamHandler(sys.stdout)
    if formato_efectivo == "json":
        manejador.setFormatter(FormateadorJSON())
    else:
        manejador.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

    raiz = logging.getLogger()
    raiz.handlers.clear()
    raiz.addHandler(manejador)
    raiz.setLevel(nivel_efectivo)

    # Reduce el ruido de librerias de terceros.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def obtener_logger(nombre: str) -> logging.Logger:
    """Devuelve un logger con el nombre indicado."""
    return logging.getLogger(nombre)
