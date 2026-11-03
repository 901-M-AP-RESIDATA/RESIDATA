"""Esquemas de contenedores (nodos ESP32-CAM)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

EstadoContenedor = Literal["activo", "inactivo", "mantenimiento"]


class ContenedorLeer(BaseModel):
    """Contenedor expuesto por el API (sin la API key)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    ubicacion: str
    estado: str
    ultima_conexion: datetime | None = None
    fecha_creacion: datetime


class ContenedorConApiKey(ContenedorLeer):
    """Contenedor recien creado o regenerado: incluye la API key en claro.

    La API key solo se devuelve UNA vez; el backend almacena su hash.
    """

    api_key: str


class ContenedorCrear(BaseModel):
    """Datos para registrar un contenedor."""

    nombre: str = Field(min_length=1, max_length=100)
    ubicacion: str = Field(min_length=1, max_length=200)
    estado: EstadoContenedor = "activo"


class ContenedorActualizar(BaseModel):
    """Datos opcionales para actualizar un contenedor."""

    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    ubicacion: str | None = Field(default=None, min_length=1, max_length=200)
    estado: EstadoContenedor | None = None


class EstadoContenedorDetalle(BaseModel):
    """Detalle ampliado de un contenedor (para la vista de detalle)."""

    id: int
    nombre: str
    ubicacion: str
    estado: str
    ultima_conexion: datetime | None = None
    total_clasificaciones: int
    ultima_clasificacion: datetime | None = None
    ultima_categoria: str | None = None
