"""Servicio de gestion de usuarios del panel web."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.excepciones import ErrorConflicto, ErrorDatos, ErrorNoEncontrado
from app.core.seguridad import hashear_contrasena
from app.db.modelos import Rol, Usuario
from app.schemas.usuario import UsuarioActualizar, UsuarioCrear


def _normalizar_correo(correo: str) -> str:
    return correo.strip().lower()


def _obtener_rol(db: Session, rol_id: int) -> Rol:
    rol = db.get(Rol, rol_id)
    if rol is None:
        raise ErrorDatos("El rol indicado no existe.")
    return rol


def _correo_ocupado(db: Session, correo: str, excluir_id: int | None = None) -> bool:
    consulta = select(Usuario.id).where(func.lower(Usuario.correo) == _normalizar_correo(correo))
    if excluir_id is not None:
        consulta = consulta.where(Usuario.id != excluir_id)
    return db.scalar(consulta) is not None


def listar(db: Session, pagina: int, limite: int) -> tuple[list[Usuario], int]:
    """Devuelve una pagina de usuarios ordenados por id."""
    total = db.scalar(select(func.count()).select_from(Usuario)) or 0
    items = list(
        db.scalars(
            select(Usuario).order_by(Usuario.id).offset((pagina - 1) * limite).limit(limite)
        )
    )
    return items, total


def obtener(db: Session, usuario_id: int) -> Usuario:
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise ErrorNoEncontrado("El usuario no existe.")
    return usuario


def obtener_por_correo(db: Session, correo: str) -> Usuario | None:
    return db.scalar(select(Usuario).where(func.lower(Usuario.correo) == _normalizar_correo(correo)))


def crear(db: Session, datos: UsuarioCrear) -> Usuario:
    if _correo_ocupado(db, datos.correo):
        raise ErrorConflicto("Ya existe un usuario con ese correo.")
    rol = _obtener_rol(db, datos.rol_id)

    usuario = Usuario(
        nombre=datos.nombre.strip(),
        correo=_normalizar_correo(datos.correo),
        contrasena_hash=hashear_contrasena(datos.contrasena),
        rol_id=rol.id,
        activo=datos.activo,
    )
    db.add(usuario)
    db.flush()
    db.refresh(usuario)
    return usuario


def actualizar(db: Session, usuario_id: int, datos: UsuarioActualizar) -> Usuario:
    usuario = obtener(db, usuario_id)

    if datos.correo is not None and _correo_ocupado(db, datos.correo, excluir_id=usuario_id):
        raise ErrorConflicto("Ya existe un usuario con ese correo.")
    if datos.rol_id is not None:
        usuario.rol_id = _obtener_rol(db, datos.rol_id).id
    if datos.nombre is not None:
        usuario.nombre = datos.nombre.strip()
    if datos.correo is not None:
        usuario.correo = _normalizar_correo(datos.correo)
    if datos.contrasena:
        usuario.contrasena_hash = hashear_contrasena(datos.contrasena)
    if datos.activo is not None:
        usuario.activo = datos.activo

    db.flush()
    db.refresh(usuario)
    return usuario


def eliminar(db: Session, usuario_id: int, usuario_actual: Usuario) -> None:
    if usuario_id == usuario_actual.id:
        raise ErrorDatos("No puedes eliminar tu propio usuario.")
    usuario = obtener(db, usuario_id)
    db.delete(usuario)
    db.flush()
