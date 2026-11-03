"""Endpoints de consulta del historico de clasificaciones."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone

from fastapi import APIRouter, Query
from sqlalchemy import func, select

from app.core.deps import SesionBd, UsuarioActual
from app.db.modelos import VistaHistoricoDetalle
from app.schemas.comun import RespuestaPaginada, construir_paginada
from app.schemas.historico import HistoricoClasificacionLeer

router = APIRouter(prefix="/historico", tags=["Historico"])

Vista = VistaHistoricoDetalle


def _a_lectura(registro: VistaHistoricoDetalle) -> HistoricoClasificacionLeer:
    return HistoricoClasificacionLeer(
        id=registro.clasificacion_id,
        fecha_hora=registro.fecha_hora,
        contenedor_id=registro.contenedor_id,
        categoria_id=registro.categoria_id,
        confianza=float(registro.confianza),
        angulo=registro.angulo,
        ruta_imagen=registro.ruta_imagen,
        tiempo_inferencia_ms=registro.tiempo_inferencia_ms,
        corregida_manualmente=registro.corregida_manualmente,
        categoria_nombre=registro.categoria_nombre,
        contenedor_nombre=registro.contenedor_nombre,
    )


@router.get("", response_model=RespuestaPaginada[HistoricoClasificacionLeer], summary="Listar historico")
def listar_historico(
    base_datos: SesionBd,
    _usuario: UsuarioActual,
    fecha_desde: date | None = Query(default=None),
    fecha_hasta: date | None = Query(default=None),
    categoria: str | None = Query(default=None),
    contenedor_id: int | None = Query(default=None, ge=1),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=20, ge=1, le=1000),
) -> RespuestaPaginada[HistoricoClasificacionLeer]:
    """Devuelve el historico filtrado y paginado (mas reciente primero)."""
    condiciones = []
    if fecha_desde is not None:
        inicio = datetime.combine(fecha_desde, time.min, tzinfo=timezone.utc)
        condiciones.append(Vista.fecha_hora >= inicio)
    if fecha_hasta is not None:
        fin = datetime.combine(fecha_hasta + timedelta(days=1), time.min, tzinfo=timezone.utc)
        condiciones.append(Vista.fecha_hora < fin)
    if categoria:
        condiciones.append(func.lower(Vista.categoria_nombre) == categoria.strip().lower())
    if contenedor_id is not None:
        condiciones.append(Vista.contenedor_id == contenedor_id)

    total = base_datos.scalar(
        select(func.count()).select_from(Vista).where(*condiciones)
    ) or 0

    registros = base_datos.scalars(
        select(Vista)
        .where(*condiciones)
        .order_by(Vista.fecha_hora.desc())
        .offset((pagina - 1) * limite)
        .limit(limite)
    ).all()

    return construir_paginada(
        [_a_lectura(registro) for registro in registros], int(total), pagina, limite
    )
