"""Esquemas de usuarios del panel web."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.rol import RolLeer

# Formato de correo simple, coherente con la restriccion de la base de datos.
PATRON_CORREO = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class UsuarioLeer(BaseModel):
    """Usuario expuesto por el API (nunca incluye la contrasena)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    correo: str
    rol_id: int
    rol: RolLeer | None = None
    activo: bool
    fecha_creacion: datetime
    ultimo_acceso: datetime | None = None


class UsuarioCrear(BaseModel):
    """Datos para crear un usuario."""

    nombre: str = Field(min_length=1, max_length=120)
    correo: str = Field(min_length=3, max_length=180, pattern=PATRON_CORREO)
    contrasena: str = Field(min_length=6, max_length=128)
    rol_id: int
    activo: bool = True


class UsuarioActualizar(BaseModel):
    """Datos opcionales para actualizar un usuario."""

    nombre: str | None = Field(default=None, min_length=1, max_length=120)
    correo: str | None = Field(default=None, min_length=3, max_length=180, pattern=PATRON_CORREO)
    contrasena: str | None = Field(default=None, min_length=6, max_length=128)
    rol_id: int | None = None
    activo: bool | None = None
