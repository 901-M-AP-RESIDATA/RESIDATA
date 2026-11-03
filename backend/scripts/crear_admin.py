"""Crea el usuario administrador inicial de ResiData (idempotente).

Uso (desde la carpeta ``backend``)::

    python scripts/crear_admin.py

Toma las credenciales de las variables ``ADMIN_NOMBRE``, ``ADMIN_CORREO`` y
``ADMIN_CONTRASENA`` del archivo ``.env``.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Permite importar el paquete `app` al ejecutar el script directamente.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import func, select  # noqa: E402

from app.core.config import obtener_configuracion  # noqa: E402
from app.core.logging import configurar_logging, obtener_logger  # noqa: E402
from app.core.seguridad import hashear_contrasena  # noqa: E402
from app.db.modelos import Rol, Usuario  # noqa: E402
from app.db.sesion import sesion_ambito  # noqa: E402


def main() -> int:
    config = obtener_configuracion()
    configurar_logging()
    logger = obtener_logger("scripts.crear_admin")

    with sesion_ambito() as db:
        rol = db.scalar(select(Rol).where(Rol.nombre == "administrador"))
        if rol is None:
            logger.error(
                "No existe el rol 'administrador'. Ejecuta las migraciones "
                "(alembic upgrade head) o el script 02_datos_iniciales.sql."
            )
            return 1

        correo = config.admin_correo.strip().lower()
        existente = db.scalar(
            select(Usuario).where(func.lower(Usuario.correo) == correo)
        )
        if existente is not None:
            logger.info("El administrador '%s' ya existe (id=%s).", correo, existente.id)
            return 0

        admin = Usuario(
            nombre=config.admin_nombre.strip(),
            correo=correo,
            contrasena_hash=hashear_contrasena(config.admin_contrasena),
            rol_id=rol.id,
            activo=True,
        )
        db.add(admin)
        db.flush()
        logger.info("Administrador creado: %s (id=%s).", correo, admin.id)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
