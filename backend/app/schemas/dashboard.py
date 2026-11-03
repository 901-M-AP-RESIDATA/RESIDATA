"""Esquemas del resumen del dashboard."""

from __future__ import annotations

from pydantic import BaseModel

from app.schemas.historico import HistoricoClasificacionLeer


class ConteoCategoria(BaseModel):
    """Total de clasificaciones por categoria."""

    categoria: str
    total: int


class ConteoDia(BaseModel):
    """Total de clasificaciones por dia (YYYY-MM-DD)."""

    dia: str
    total: int


class ResumenDashboard(BaseModel):
    """Resumen agregado que alimenta el panel principal."""

    total_hoy: int
    total_historico: int
    por_categoria: list[ConteoCategoria]
    por_dia: list[ConteoDia]
    confianza_promedio: float
    alertas_pendientes: int
    ultimas: list[HistoricoClasificacionLeer]
