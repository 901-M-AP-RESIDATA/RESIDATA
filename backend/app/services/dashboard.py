"""Servicio de agregaciones para el dashboard."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.db.modelos import Alerta, HistoricoClasificacion, VistaHistoricoDetalle
from app.schemas.dashboard import ConteoCategoria, ConteoDia, ResumenDashboard
from app.schemas.historico import HistoricoClasificacionLeer

DIAS_GRAFICA = 7
LIMITE_ULTIMAS = 8


def _items_por_categoria(db: Session) -> list[ConteoCategoria]:
    filas = db.execute(
        text(
            """
            SELECT c.nombre AS categoria, COUNT(h.id) AS total
            FROM categorias_residuo c
            LEFT JOIN historico_clasificaciones h ON h.categoria_id = c.id
            GROUP BY c.id, c.nombre
            ORDER BY c.id
            """
        )
    ).all()
    return [ConteoCategoria(categoria=fila.categoria, total=int(fila.total)) for fila in filas]


def _items_por_dia(db: Session) -> list[ConteoDia]:
    filas = db.execute(
        text(
            """
            SELECT to_char(d.dia, 'YYYY-MM-DD') AS dia, COUNT(h.id) AS total
            FROM generate_series(
                    (CURRENT_DATE - INTERVAL '6 days')::date,
                    CURRENT_DATE,
                    INTERVAL '1 day'
                 ) AS d(dia)
            LEFT JOIN historico_clasificaciones h
                   ON h.fecha_hora >= d.dia AND h.fecha_hora < d.dia + INTERVAL '1 day'
            GROUP BY d.dia
            ORDER BY d.dia
            """
        )
    ).all()
    return [ConteoDia(dia=fila.dia, total=int(fila.total)) for fila in filas]


def _ultimas(db: Session) -> list[HistoricoClasificacionLeer]:
    registros = db.scalars(
        select(VistaHistoricoDetalle)
        .order_by(VistaHistoricoDetalle.fecha_hora.desc())
        .limit(LIMITE_ULTIMAS)
    )
    return [
        HistoricoClasificacionLeer(
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
        for registro in registros
    ]


def obtener_resumen(db: Session) -> ResumenDashboard:
    """Construye el resumen agregado que alimenta el dashboard."""
    total_hoy = db.scalar(
        select(func.count())
        .select_from(HistoricoClasificacion)
        .where(func.date(HistoricoClasificacion.fecha_hora) == func.current_date())
    ) or 0
    total_historico = db.scalar(select(func.count()).select_from(HistoricoClasificacion)) or 0

    promedio = db.scalar(select(func.avg(HistoricoClasificacion.confianza)))
    confianza_promedio = round(float(promedio), 4) if promedio is not None else 0.0

    alertas_pendientes = db.scalar(
        select(func.count()).select_from(Alerta).where(Alerta.atendida.is_(False))
    ) or 0

    return ResumenDashboard(
        total_hoy=int(total_hoy),
        total_historico=int(total_historico),
        por_categoria=_items_por_categoria(db),
        por_dia=_items_por_dia(db),
        confianza_promedio=confianza_promedio,
        alertas_pendientes=int(alertas_pendientes),
        ultimas=_ultimas(db),
    )
