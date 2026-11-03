"""Orquestacion del flujo de clasificacion de una lectura IoT.

Pasos: clasificar la imagen, aplicar el umbral de confianza, almacenar la
imagen, persistir el historico, actualizar el contenedor, generar alertas y
notificar por WebSocket.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import obtener_configuracion
from app.core.excepciones import ErrorDatos
from app.core.logging import obtener_logger
from app.db.modelos import (
    Alerta,
    CategoriaResiduo,
    Contenedor,
    HistoricoClasificacion,
    ReglaServo,
)
from app.schemas.alerta import AlertaLeer
from app.schemas.dispositivo import RespuestaClasificacion
from app.schemas.historico import HistoricoClasificacionLeer
from app.services import almacenamiento, ia_yolo
from app.services.tiempo_real import gestor

logger = obtener_logger(__name__)

NIVEL_PELIGROSO = 3


def _obtener_categoria(db: Session, nombre: str) -> CategoriaResiduo:
    categoria = db.scalar(select(CategoriaResiduo).where(CategoriaResiduo.nombre == nombre))
    if categoria is None:
        raise ErrorDatos(f"La categoria '{nombre}' no existe en el catalogo.")
    return categoria


def _obtener_angulo(db: Session, categoria_id: int) -> int:
    regla = db.scalar(select(ReglaServo).where(ReglaServo.categoria_id == categoria_id))
    if regla is not None:
        return regla.angulo
    regla_defecto = db.scalar(select(ReglaServo).where(ReglaServo.es_por_defecto.is_(True)))
    return regla_defecto.angulo if regla_defecto is not None else 0


def _a_lectura(
    historico: HistoricoClasificacion,
    categoria: CategoriaResiduo,
    contenedor: Contenedor,
) -> HistoricoClasificacionLeer:
    return HistoricoClasificacionLeer(
        id=historico.id,
        fecha_hora=historico.fecha_hora,
        contenedor_id=historico.contenedor_id,
        categoria_id=historico.categoria_id,
        confianza=float(historico.confianza),
        angulo=historico.angulo,
        ruta_imagen=historico.ruta_imagen,
        tiempo_inferencia_ms=historico.tiempo_inferencia_ms,
        corregida_manualmente=historico.corregida_manualmente,
        categoria_nombre=categoria.nombre,
        contenedor_nombre=contenedor.nombre,
    )


def _a_alerta_leer(alerta: Alerta, categoria_nombre: str, contenedor_nombre: str) -> AlertaLeer:
    return AlertaLeer(
        id=alerta.id,
        historico_id=alerta.historico_id,
        contenedor_id=alerta.contenedor_id,
        tipo=alerta.tipo,
        mensaje=alerta.mensaje,
        atendida=alerta.atendida,
        fecha_creacion=alerta.fecha_creacion,
        fecha_atencion=alerta.fecha_atencion,
        atendida_por=alerta.atendida_por,
        contenedor_nombre=contenedor_nombre,
        categoria_nombre=categoria_nombre,
    )


def _difundir_clasificacion(lectura: HistoricoClasificacionLeer) -> None:
    gestor.difundir(
        {"tipo": "nueva_clasificacion", "data": lectura.model_dump(mode="json")}
    )


def _difundir_alerta(alerta: AlertaLeer) -> None:
    gestor.difundir({"tipo": "alerta_peligroso", "data": alerta.model_dump(mode="json")})


def procesar_lectura(
    db: Session,
    contenedor: Contenedor,
    imagen: bytes,
    extension: str = "jpg",
) -> RespuestaClasificacion:
    """Procesa una imagen enviada por un nodo IoT y devuelve el resultado."""
    config = obtener_configuracion()
    resultado = ia_yolo.clasificar(imagen)

    es_baja_confianza = resultado.confianza < config.umbral_confianza
    categoria_nombre = (
        config.categoria_baja_confianza if es_baja_confianza else resultado.categoria_nombre
    )
    categoria = _obtener_categoria(db, categoria_nombre)
    angulo = _obtener_angulo(db, categoria.id)

    ruta_imagen = almacenamiento.guardar_imagen(imagen, extension=extension)

    ahora = datetime.now(tz=timezone.utc)
    historico = HistoricoClasificacion(
        fecha_hora=ahora,
        contenedor_id=contenedor.id,
        categoria_id=categoria.id,
        confianza=resultado.confianza,
        angulo=angulo,
        ruta_imagen=ruta_imagen,
        tiempo_inferencia_ms=resultado.tiempo_inferencia_ms,
        corregida_manualmente=False,
    )
    db.add(historico)
    contenedor.ultima_conexion = ahora
    db.flush()
    db.refresh(historico)

    alertas_creadas: list[Alerta] = []

    if categoria.nivel_peligrosidad >= NIVEL_PELIGROSO:
        alerta = Alerta(
            historico_id=historico.id,
            contenedor_id=contenedor.id,
            tipo="residuo_peligroso",
            mensaje=(
                f"Residuo peligroso detectado (confianza {resultado.confianza}). "
                "Requiere atencion inmediata."
            ),
            fecha_creacion=ahora,
        )
        db.add(alerta)
        alertas_creadas.append(alerta)

    if es_baja_confianza:
        alerta = Alerta(
            historico_id=historico.id,
            contenedor_id=contenedor.id,
            tipo="baja_confianza",
            mensaje=(
                f"Clasificacion con baja confianza ({resultado.confianza}). "
                "Revisar manualmente."
            ),
            fecha_creacion=ahora,
        )
        db.add(alerta)
        alertas_creadas.append(alerta)

    db.flush()

    lectura = _a_lectura(historico, categoria, contenedor)
    _difundir_clasificacion(lectura)

    alerta_generada = False
    for alerta in alertas_creadas:
        db.refresh(alerta)
        if alerta.tipo == "residuo_peligroso":
            _difundir_alerta(_a_alerta_leer(alerta, categoria.nombre, contenedor.nombre))
            alerta_generada = True

    logger.info(
        "Clasificacion %s: %s (confianza=%.4f, contenedor=%s)",
        historico.id,
        categoria.nombre,
        resultado.confianza,
        contenedor.nombre,
    )

    return RespuestaClasificacion(
        historico=lectura,
        categoria_id=categoria.id,
        categoria_nombre=categoria.nombre,
        color_bolsa=categoria.color_bolsa,
        angulo=angulo,
        confianza=float(resultado.confianza),
        tiempo_inferencia_ms=resultado.tiempo_inferencia_ms,
        alerta_generada=alerta_generada,
    )
