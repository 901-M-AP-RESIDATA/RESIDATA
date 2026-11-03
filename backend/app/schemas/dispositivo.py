"""Esquemas de ingesta desde nodos IoT (ESP32-CAM)."""

from __future__ import annotations

from pydantic import BaseModel

from app.schemas.historico import HistoricoClasificacionLeer


class RespuestaClasificacion(BaseModel):
    """Resultado devuelto al nodo IoT tras procesar una imagen.

    Incluye la categoria, el angulo que debe aplicar el servomotor SG90 y
    el identificador del registro creado en el historico.
    """

    historico: HistoricoClasificacionLeer
    categoria_id: int
    categoria_nombre: str
    color_bolsa: str
    angulo: int
    confianza: float
    tiempo_inferencia_ms: int
    alerta_generada: bool
