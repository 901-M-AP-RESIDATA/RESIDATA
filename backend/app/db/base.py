"""Clase base declarativa de SQLAlchemy 2.0.

Los nombres de las restricciones se declaran de forma explicita en cada
modelo para que coincidan exactamente con el esquema creado por los
scripts de ``/database``.
"""

from __future__ import annotations

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# Esquema por defecto de la base ResiData.
ESQUEMA = "public"


class Base(DeclarativeBase):
    """Clase base de todos los modelos ORM de ResiData."""

    metadata = MetaData(schema=ESQUEMA)
