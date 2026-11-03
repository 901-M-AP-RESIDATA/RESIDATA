"""Esquemas del catalogo de categorias de residuo."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class CategoriaResiduoLeer(BaseModel):
    """Categoria de residuo (Organico, Inorganico, Peligroso)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    nivel_peligrosidad: int
    color_bolsa: str
    descripcion: str | None = None
