"""Endpoint de resumen agregado del dashboard."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.deps import SesionBd, UsuarioActual
from app.schemas.dashboard import ResumenDashboard
from app.services import dashboard as servicio_dashboard

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/resumen", response_model=ResumenDashboard, summary="Resumen del dashboard")
def obtener_resumen(base_datos: SesionBd, _usuario: UsuarioActual) -> ResumenDashboard:
    """Devuelve KPIs, distribucion por categoria, tendencia y ultimas lecturas."""
    return servicio_dashboard.obtener_resumen(base_datos)
