"""Esquemas de alertas."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

TipoAlerta = Literal[
    "residuo_peligroso",
    "baja_confianza",
    "error_contenedor",
    "sistema",
]


class AlertaLeer(BaseModel):
    """Alerta operativa expuesta por el API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    historico_id: int
    contenedor_id: int
    tipo: str
    mensaje: str
    atendida: bool
    fecha_creacion: datetime
    fecha_atencion: datetime | None = None
    atendida_por: int | None = None
    contenedor_nombre: str | None = None
    categoria_nombre: str | None = None


class AlertaActualizar(BaseModel):
    """Permite marcar una alerta como atendida o reabrirla."""

    atendida: bool = True
