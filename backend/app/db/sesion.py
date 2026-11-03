"""Sesion y motor de base de datos (SQLAlchemy 2.0 + psycopg 3).

El motor usa un pool de conexiones preparado para escrituras concurrentes
desde varios nodos IoT: ``pool_pre_ping`` valida conexiones antes de
usarlas y ``pool_size``/``max_overflow`` permiten atencion simultanea.
"""

from __future__ import annotations

from collections.abc import Generator, Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import obtener_configuracion

_config = obtener_configuracion()

motor: Engine = create_engine(
    _config.database_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=1800,
    future=True,
)

FabricaSesiones = sessionmaker(
    bind=motor,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=Session,
)


def obtener_db() -> Generator[Session, None, None]:
    """Dependencia de FastAPI que entrega una sesion por peticion.

    Hace commit si la peticion termina correctamente y rollback si se
    produce cualquier excepcion.
    """
    sesion = FabricaSesiones()
    try:
        yield sesion
        sesion.commit()
    except Exception:
        sesion.rollback()
        raise
    finally:
        sesion.close()


@contextmanager
def sesion_ambito() -> Iterator[Session]:
    """Gestor de contexto para usar una sesion fuera de FastAPI (scripts)."""
    sesion = FabricaSesiones()
    try:
        yield sesion
        sesion.commit()
    except Exception:
        sesion.rollback()
        raise
    finally:
        sesion.close()
