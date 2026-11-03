"""Esquemas compartidos: paginacion y respuestas genericas."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class RespuestaPaginada(BaseModel, Generic[T]):
    """Respuesta paginada estandar del API (misma forma que el frontend)."""

    items: list[T]
    total: int
    pagina: int
    limite: int
    paginas: int


class MensajeRespuesta(BaseModel):
    """Respuesta simple con un mensaje informativo."""

    mensaje: str


class ParametrosPaginacion(BaseModel):
    """Parametros comunes de paginacion."""

    pagina: int = Field(default=1, ge=1)
    limite: int = Field(default=20, ge=1, le=1000)

    @property
    def offset(self) -> int:
        return (self.pagina - 1) * self.limite


def construir_paginada(
    items: list[T], total: int, pagina: int, limite: int
) -> RespuestaPaginada[T]:
    """Construye una respuesta paginada calculando el total de paginas."""
    paginas = (total + limite - 1) // limite if limite else 0
    return RespuestaPaginada[T](
        items=items,
        total=total,
        pagina=pagina,
        limite=limite,
        paginas=max(1, paginas),
    )
