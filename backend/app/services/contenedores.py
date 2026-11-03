"""Servicio de gestion de contenedores (nodos ESP32-CAM)."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.excepciones import ErrorConflicto, ErrorNoEncontrado
from app.core.seguridad import generar_api_key, hashear_api_key
from app.db.modelos import CategoriaResiduo, Contenedor, HistoricoClasificacion
from app.schemas.contenedor import (
    ContenedorActualizar,
    ContenedorCrear,
    EstadoContenedorDetalle,
)


def _nombre_ocupado(db: Session, nombre: str, excluir_id: int | None = None) -> bool:
    consulta = select(Contenedor.id).where(func.lower(Contenedor.nombre) == nombre.strip().lower())
    if excluir_id is not None:
        consulta = consulta.where(Contenedor.id != excluir_id)
    return db.scalar(consulta) is not None


def listar(db: Session, pagina: int, limite: int) -> tuple[list[Contenedor], int]:
    """Devuelve una pagina de contenedores ordenados por id."""
    total = db.scalar(select(func.count()).select_from(Contenedor)) or 0
    items = list(
        db.scalars(
            select(Contenedor).order_by(Contenedor.id).offset((pagina - 1) * limite).limit(limite)
        )
    )
    return items, total


def obtener(db: Session, contenedor_id: int) -> Contenedor:
    contenedor = db.get(Contenedor, contenedor_id)
    if contenedor is None:
        raise ErrorNoEncontrado("El contenedor no existe.")
    return contenedor


def obtener_detalle(db: Session, contenedor_id: int) -> EstadoContenedorDetalle:
    contenedor = obtener(db, contenedor_id)

    total = db.scalar(
        select(func.count())
        .select_from(HistoricoClasificacion)
        .where(HistoricoClasificacion.contenedor_id == contenedor_id)
    ) or 0

    ultimo = db.scalar(
        select(HistoricoClasificacion)
        .where(HistoricoClasificacion.contenedor_id == contenedor_id)
        .order_by(HistoricoClasificacion.fecha_hora.desc())
        .limit(1)
    )

    ultima_categoria: str | None = None
    if ultimo is not None:
        ultima_categoria = db.scalar(
            select(CategoriaResiduo.nombre).where(CategoriaResiduo.id == ultimo.categoria_id)
        )

    return EstadoContenedorDetalle(
        id=contenedor.id,
        nombre=contenedor.nombre,
        ubicacion=contenedor.ubicacion,
        estado=contenedor.estado,
        ultima_conexion=contenedor.ultima_conexion,
        total_clasificaciones=total,
        ultima_clasificacion=ultimo.fecha_hora if ultimo else None,
        ultima_categoria=ultima_categoria,
    )


def _crear_api_key_unica(db: Session, intentos: int = 5) -> str:
    """Genera una API key en claro cuyo hash no colisione con otro contenedor."""
    for _ in range(intentos):
        api_key = generar_api_key()
        existe = db.scalar(
            select(Contenedor.id).where(Contenedor.api_key_hash == hashear_api_key(api_key))
        )
        if existe is None:
            return api_key
    raise ErrorConflicto("No se pudo generar una API key unica, intentalo de nuevo.")


def crear(db: Session, datos: ContenedorCrear) -> tuple[Contenedor, str]:
    if _nombre_ocupado(db, datos.nombre):
        raise ErrorConflicto("Ya existe un contenedor con ese nombre.")
    api_key = _crear_api_key_unica(db)
    contenedor = Contenedor(
        nombre=datos.nombre.strip(),
        ubicacion=datos.ubicacion.strip(),
        estado=datos.estado,
        api_key_hash=hashear_api_key(api_key),
    )
    db.add(contenedor)
    db.flush()
    db.refresh(contenedor)
    return contenedor, api_key


def actualizar(db: Session, contenedor_id: int, datos: ContenedorActualizar) -> Contenedor:
    contenedor = obtener(db, contenedor_id)
    if datos.nombre is not None:
        if _nombre_ocupado(db, datos.nombre, excluir_id=contenedor_id):
            raise ErrorConflicto("Ya existe un contenedor con ese nombre.")
        contenedor.nombre = datos.nombre.strip()
    if datos.ubicacion is not None:
        contenedor.ubicacion = datos.ubicacion.strip()
    if datos.estado is not None:
        contenedor.estado = datos.estado
    db.flush()
    db.refresh(contenedor)
    return contenedor


def eliminar(db: Session, contenedor_id: int) -> None:
    contenedor = obtener(db, contenedor_id)
    db.delete(contenedor)
    db.flush()


def regenerar_clave(db: Session, contenedor_id: int) -> tuple[Contenedor, str]:
    contenedor = obtener(db, contenedor_id)
    api_key = _crear_api_key_unica(db)
    contenedor.api_key_hash = hashear_api_key(api_key)
    db.flush()
    db.refresh(contenedor)
    return contenedor, api_key
