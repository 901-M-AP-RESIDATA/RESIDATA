"""Servicio de clasificacion de residuos con IA.

En esta version el backend funciona en **MODO SIMULADO**: si el archivo de
pesos indicado por ``RUTA_MODELO`` no existe, se genera una clasificacion
aleatoria ponderada (Organico 45 %, Inorganico 35 %, Peligroso 20 %). Si el
archivo existe y las dependencias de ``requirements-ml.txt`` estan
instaladas, se usa el modelo YOLO real.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from pathlib import Path

from app.core.config import obtener_configuracion
from app.core.logging import obtener_logger

logger = obtener_logger(__name__)

# Pesos de la simulacion (deben sumar 1.0).
_PESOS_SIMULADOS: tuple[tuple[str, float], ...] = (
    ("Organico", 0.45),
    ("Inorganico", 0.35),
    ("Peligroso", 0.20),
)


@dataclass(slots=True)
class ResultadoInferencia:
    """Resultado crudo de la clasificacion (antes de aplicar el umbral)."""

    categoria_nombre: str
    confianza: float
    tiempo_inferencia_ms: int
    simulada: bool


class DetectorResiduos:
    """Detector de residuos con carga perezosa del modelo."""

    def __init__(self) -> None:
        self._modelo = None
        self._intentado = False

    def _cargar_modelo(self) -> None:
        if self._intentado:
            return
        self._intentado = True
        config = obtener_configuracion()
        ruta = Path(config.ruta_modelo)
        if not ruta.exists():
            logger.warning(
                "Pesos YOLO no encontrados en %s. El backend funciona en MODO SIMULADO.",
                ruta,
            )
            return
        try:  # pragma: no cover - depende de dependencias opcionales
            from ultralytics import YOLO  # type: ignore[import-not-found]

            self._modelo = YOLO(str(ruta))
            logger.info("Modelo YOLO cargado correctamente desde %s.", ruta)
        except Exception as exc:  # noqa: BLE001
            logger.warning("No se pudo cargar el modelo YOLO (%s). MODO SIMULADO.", exc)

    @property
    def simulada(self) -> bool:
        self._cargar_modelo()
        return self._modelo is None

    def clasificar(self, imagen: bytes) -> ResultadoInferencia:
        """Clasifica una imagen y devuelve el resultado crudo."""
        self._cargar_modelo()
        if self._modelo is None:
            return self._clasificar_simulado()
        return self._clasificar_real(imagen)  # pragma: no cover

    def _clasificar_simulado(self) -> ResultadoInferencia:
        inicio = time.perf_counter()
        categorias = [nombre for nombre, _ in _PESOS_SIMULADOS]
        pesos = [peso for _, peso in _PESOS_SIMULADOS]
        categoria = random.choices(categorias, weights=pesos, k=1)[0]
        confianza = round(0.55 + random.random() * 0.44, 4)
        tiempo = max(1, int((time.perf_counter() - inicio) * 1000) + random.randint(180, 600))
        return ResultadoInferencia(
            categoria_nombre=categoria,
            confianza=confianza,
            tiempo_inferencia_ms=tiempo,
            simulada=True,
        )

    def _clasificar_real(self, imagen: bytes) -> ResultadoInferencia:  # pragma: no cover
        """Inferencia real con YOLO. Requiere requirements-ml.txt."""
        from io import BytesIO  # noqa: PLC0415

        from PIL import Image  # noqa: PLC0415

        inicio = time.perf_counter()
        imagen_pil = Image.open(BytesIO(imagen)).convert("RGB")
        resultados = self._modelo.predict(imagen_pil, verbose=False)
        resultado = resultados[0]

        mejor_nombre = "Organico"
        mejor_confianza = 0.0
        for caja in getattr(resultado, "boxes", []):
            confianza = float(caja.conf[0])
            if confianza > mejor_confianza:
                mejor_confianza = confianza
                clase = int(caja.cls[0])
                mejor_nombre = self._mapear_clase(resultado.names.get(clase, ""))

        tiempo = int((time.perf_counter() - inicio) * 1000)
        return ResultadoInferencia(
            categoria_nombre=mejor_nombre,
            confianza=round(mejor_confianza, 4),
            tiempo_inferencia_ms=tiempo,
            simulada=False,
        )

    @staticmethod
    def _mapear_clase(etiqueta: str) -> str:  # pragma: no cover
        """Traduce etiquetas del dataset a las tres categorias del sistema."""
        mapa = {
            "organico": "Organico",
            "organi": "Organico",
            "food": "Organico",
            "vidrio": "Inorganico",
            "glass": "Inorganico",
            "plastico": "Inorganico",
            "plastic": "Inorganico",
            "metal": "Inorganico",
            "papel": "Inorganico",
            "paper": "Inorganico",
            "bateria": "Peligroso",
            "battery": "Peligroso",
            "peligroso": "Peligroso",
        }
        return mapa.get(etiqueta.strip().lower(), "Peligroso")


# Instancia unica (carga perezosa del modelo).
detector = DetectorResiduos()


def clasificar(imagen: bytes) -> ResultadoInferencia:
    """Clasifica una imagen usando el detector global."""
    return detector.clasificar(imagen)
