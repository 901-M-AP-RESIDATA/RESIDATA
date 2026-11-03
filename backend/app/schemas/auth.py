"""Esquemas de autenticacion y tokens."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RespuestaToken(BaseModel):
    """Par de tokens devuelto al iniciar sesion o refrescar."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class SolicitudRefresco(BaseModel):
    """Cuerpo para renovar el token de acceso."""

    refresh_token: str = Field(min_length=1)
