"""Endpoints de consulta y atencion de alertas."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Query
from sqlalchemy import func, select

from app.core.deps import SesionBd, UsuarioActual
from app.core.excepciones import ErrorNoEncontrado
from app.db.modelos import Alerta, CategoriaResiduo, Contenedor, HistoricoClasificacion
from app.schemas.alerta import AlertaActualizar, AlertaLeer
from app.schemas.comun import RespuestaPaginada, construir_paginada

router = APIRouter(prefix="/alertas", tags=["Alertas"])


def _a_leer(
    alerta: Alerta, contenedor_nombre: str | None, categoria_nombre: str | None
) -> AlertaLeer:
    return AlertaLeer(
        id=alerta.id,
        historico_id=alerta.historico_id,
        contenedor_id=alerta.contenedor_id,
        tipo=alerta.tipo,
        mensaje=alerta.mensaje,
        atendida=alerta.atendida,
        fecha_creacion=alerta.fecha_creacion,
        fecha_atencion=alerta.fecha_atencion,
        atendida_por=alerta.atendida_por,
        contenedor_nombre=contenedor_nombre,
        categoria_nombre=categoria_nombre,
    )


def _consulta_base():
    return (
        select(Alerta, Contenedor.nombre, CategoriaResiduo.nombre)
        .join(Contenedor, Alerta.contenedor_id == Contenedor.id)
        .join(HistoricoClasificacion, Alerta.historico_id == HistoricoClasificacion.id)
        .join(CategoriaResiduo, HistoricoClasificacion.categoria_id == CategoriaResiduo.id)
    )


@router.get("", response_model=RespuestaPaginada[AlertaLeer], summary="Listar alertas")
def listar_alertas(
    base_datos: SesionBd,
    _usuario: UsuarioActual,
    atendida: bool | None = Query(default=None),
    tipo: str | None = Query(default=None),
    contenedor_id: int | None = Query(default=None, ge=1),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=20, ge=1, le=1000),
) -> RespuestaPaginada[AlertaLeer]:
    """Devuelve las alertas filtradas y paginadas (mas reciente primero)."""
    condiciones = []
    if atendida is not None:
        condiciones.append(Alerta.atendida.is_(atendida))
    if tipo:
        condiciones.append(Alerta.tipo == tipo)
    if contenedor_id is not None:
        condiciones.append(Alerta.contenedor_id == contenedor_id)

    total = base_datos.scalar(
        select(func.count()).select_from(Alerta).where(*condiciones)
    ) or 0

    filas = base_datos.execute(
        _consulta_base()
        .where(*condiciones)
        .order_by(Alerta.fecha_creacion.desc())
        .offset((pagina - 1) * limite)
        .limit(limite)
    ).all()

    items = [_a_leer(alerta, contenedor, categoria) for alerta, contenedor, categoria in filas]
    return construir_paginada(items, int(total), pagina, limite)


@router.patch("/{alerta_id}", response_model=AlertaLeer, summary="Atender o reabrir alerta")
def actualizar_alerta(
    base_datos: SesionBd,
    usuario: UsuarioActual,
    alerta_id: int,
    datos: AlertaActualizar,
) -> AlertaLeer:
    """Marca una alerta como atendida (o la reabre) y registra el autor."""
    alerta = base_datos.get(Alerta, alerta_id)
    if alerta is None:
        raise ErrorNoEncontrado("La alerta no existe.")

    if datos.atendida:
        alerta.atendida = True
        alerta.fecha_atencion = datetime.now(tz=timezone.utc)
        alerta.atendida_por = usuario.id
    else:
        alerta.atendida = False
        alerta.fecha_atencion = None
        alerta.atendida_por = None

    base_datos.flush()
    base_datos.refresh(alerta)

    fila = base_datos.execute(
        _consulta_base().where(Alerta.id == alerta_id)
    ).one()
    return _a_leer(fila[0], fila[1], fila[2])
