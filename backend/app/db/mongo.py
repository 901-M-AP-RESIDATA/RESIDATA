"""Gestion de la conexion y operaciones en MongoDB (NoSQL).

Almacena telemetria no estructurada, eventos de hardware y auditoria
de lecturas IoT complementando a la base de datos relacional PostgreSQL.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from app.core.config import obtener_configuracion
from app.core.logging import obtener_logger

logger = obtener_logger(__name__)

_cliente_mongo: MongoClient | None = None


def obtener_cliente_mongo() -> MongoClient:
    """Devuelve la instancia singleton del cliente de MongoDB."""
    global _cliente_mongo
    if _cliente_mongo is None:
        config = obtener_configuracion()
        logger.info("Conectando a MongoDB en %s...", config.mongo_url.split("@")[-1])
        _cliente_mongo = MongoClient(
            config.mongo_url,
            serverSelectionTimeoutMS=2500,
            connectTimeoutMS=2500,
        )
    return _cliente_mongo


def obtener_mongo_db() -> Database:
    """Devuelve la base de datos de MongoDB configurada."""
    config = obtener_configuracion()
    return obtener_cliente_mongo()[config.mongo_db_nombre]


def obtener_coleccion(nombre: str) -> Collection:
    """Obtiene una coleccion especifica de MongoDB."""
    return obtener_mongo_db()[nombre]


def verificar_conexion_mongo() -> bool:
    """Verifica si MongoDB esta respondiendo correctamente."""
    try:
        cliente = obtener_cliente_mongo()
        cliente.admin.command("ping")
        return True
    except Exception as exc:  # noqa: BLE001
        logger.warning("No se pudo conectar con MongoDB: %s", exc)
        return False


def guardar_telemetria_iot(
    contenedor_id: int,
    contenedor_nombre: str,
    clasificacion_id: int,
    categoria_nombre: str,
    confianza: float,
    angulo: int,
    tiempo_inferencia_ms: int,
    alerta_generada: bool,
    metadatos_extra: dict[str, Any] | None = None,
) -> str | None:
    """Inserta un documento de telemetria IoT en la coleccion NoSQL."""
    try:
        coleccion = obtener_coleccion("telemetria_iot")
        documento = {
            "fecha_hora_utc": datetime.now(timezone.utc),
            "dispositivo": {
                "contenedor_id": contenedor_id,
                "contenedor_nombre": contenedor_nombre,
                "tipo_sensor": "ESP32-CAM OV2640 + IR FC-51",
            },
            "resultado_ia": {
                "clasificacion_id": clasificacion_id,
                "categoria": categoria_nombre,
                "confianza": confianza,
                "tiempo_inferencia_ms": tiempo_inferencia_ms,
            },
            "mecanismo": {
                "actuador": "Servomotor SG90",
                "angulo_asignado": angulo,
            },
            "alerta_emitida": alerta_generada,
            "metadatos": metadatos_extra or {},
        }
        resultado = coleccion.insert_one(documento)
        return str(resultado.inserted_id)
    except Exception as exc:  # noqa: BLE001
        logger.error("Error al persistir telemetria en MongoDB: %s", exc)
        return None


def listar_telemetria_iot(limite: int = 20) -> list[dict[str, Any]]:
    """Consulta los ultimos documentos de telemetria registrados en MongoDB."""
    try:
        coleccion = obtener_coleccion("telemetria_iot")
        cursor = coleccion.find({}, {"_id": 1, "fecha_hora_utc": 1, "dispositivo": 1, "resultado_ia": 1, "mecanismo": 1, "alerta_emitida": 1}).sort("fecha_hora_utc", -1).limit(limite)
        docs = []
        for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            if isinstance(doc.get("fecha_hora_utc"), datetime):
                doc["fecha_hora_utc"] = doc["fecha_hora_utc"].isoformat()
            docs.append(doc)
        return docs
    except Exception as exc:  # noqa: BLE001
        logger.error("Error al listar telemetria desde MongoDB: %s", exc)
        return []
