"""Esquemas del historico de clasificaciones."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HistoricoClasificacionLeer(BaseModel):
    """Clasificacion tal como la consume el panel web."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    fecha_hora: datetime
    contenedor_id: int
    categoria_id: int
    confianza: float
    angulo: int
    ruta_imagen: str
    tiempo_inferencia_ms: int
    corregida_manualmente: bool
    categoria_nombre: str | None = None
    contenedor_nombre: str | None = None
