"""Configuracion central del backend ResiData.

Toda la configuracion se lee de variables de entorno o del archivo `.env`
(ver `.env.example`). Se expone una instancia unica mediante
:func:`obtener_configuracion` para evitar relecturas.
"""

from __future__ import annotations

from functools import lru_cache
from typing import List, Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracion(BaseSettings):
    """Parametros de configuracion del backend.

    Los nombres de los campos se mapean a variables de entorno en
    MAYUSCULAS (por ejemplo ``jwt_secreto`` -> ``JWT_SECRETO``).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Aplicacion ---------------------------------------------------
    app_nombre: str = "ResiData API"
    app_version: str = "1.0.0"
    entorno: Literal["desarrollo", "produccion", "pruebas"] = "desarrollo"
    debug: bool = False

    # --- Base de datos ------------------------------------------------
    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@127.0.0.1:5432/residata",
        description="Cadena de conexion SQLAlchemy (driver psycopg 3).",
    )

    # --- Seguridad / JWT ----------------------------------------------
    jwt_secreto: str = "cambiar-este-secreto-en-produccion"
    jwt_algoritmo: str = "HS256"
    access_token_minutos: int = 30
    refresh_token_dias: int = 7
    # Origenes CORS como cadena separada por comas (o JSON) para simplificar
    # la lectura desde variables de entorno.
    cors_origenes: str = "http://localhost:5173"

    # --- IA / clasificacion -------------------------------------------
    ruta_modelo: str = "app/ml/pesos/residuos_yolo.pt"
    umbral_confianza: float = 0.60
    categoria_baja_confianza: str = "Peligroso"
    tiempo_max_inferencia_ms: int = 2000
    tamano_max_imagen_mb: int = 5

    # --- Almacenamiento ------------------------------------------------
    directorio_almacenamiento: str = "storage/imagenes"

    # --- Usuario administrador inicial --------------------------------
    admin_nombre: str = "Administrador ResiData"
    admin_correo: str = "admin@residata.local"
    admin_contrasena: str = "cambiar123"

    # --- Logging -------------------------------------------------------
    log_nivel: str = "INFO"
    log_formato: Literal["consola", "json"] = "consola"

    @property
    def origenes_cors(self) -> List[str]:
        """Devuelve los origenes CORS como lista."""
        texto = self.cors_origenes.strip()
        if not texto:
            return []
        if texto.startswith("["):
            import json

            try:
                return json.loads(texto)
            except json.JSONDecodeError:
                texto = texto.strip("[]")
        return [origen.strip() for origen in texto.split(",") if origen.strip()]

    @property
    def tamano_max_imagen_bytes(self) -> int:
        """Tamano maximo de imagen en bytes."""
        return self.tamano_max_imagen_mb * 1024 * 1024

    @property
    def es_produccion(self) -> bool:
        """Indica si el entorno es produccion."""
        return self.entorno == "produccion"


@lru_cache
def obtener_configuracion() -> Configuracion:
    """Devuelve la configuracion (cacheada) del backend."""
    return Configuracion()
