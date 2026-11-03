"""Esquemas del catalogo de roles."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class RolLeer(BaseModel):
    """Rol tal como se expone por el API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: str | None = None
