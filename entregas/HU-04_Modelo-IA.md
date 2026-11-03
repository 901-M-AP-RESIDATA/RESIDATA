# HU-04 — Procesamiento del Modelo de IA

- **ID:** HU-04
- **Nombre:** Procesamiento del Modelo de IA
- **Responsable:** Nicole
- **Prioridad:** Alta
- **Carpeta:** `HU-04_Modelo-IA`
- **Origen:** `RESIDATA completo` (copia íntegra, sin modificar el código)

## Tareas técnicas cubiertas

| Tarea técnica | Archivo(s) | Detalle |
| --- | --- | --- |
| Integración del modelo de inferencia con la aplicación | `backend/app/services/ia_yolo.py` | Clase `DetectorResiduos` con **carga perezosa** del modelo y **instancia única** (`detector`); función pública `clasificar(imagen)` |
| Pipeline de preprocesamiento de imágenes | `backend/app/services/ia_yolo.py` | `Image.open(BytesIO(imagen)).convert("RGB")` antes de `model.predict(...)`; el escalado/normalización lo aplica internamente Ultralytics |
| Inferencia para 3 categorías (Orgánico, Inorgánico, Peligroso) | `backend/app/services/ia_yolo.py` | `_mapear_clase()` traduce etiquetas del dataset a `Organico` / `Inorganico` / `Peligroso` (fallback `Peligroso`) |
| Parseo del resultado: categoría y porcentaje de confianza | `backend/app/services/ia_yolo.py` | Recorre `resultado.boxes`, toma la mayor `caja.conf[0]` y devuelve `ResultadoInferencia(categoria_nombre, confianza, tiempo_inferencia_ms, simulada)` |
| Optimización para inferencia < 2 s | `backend/app/services/ia_yolo.py`, `backend/requirements-ml.txt` | Modelo cargado una sola vez (lazy singleton), `predict(..., verbose=False)` y medición con `time.perf_counter()`; el umbral objetivo está en `TIEMPO_MAX_INFERENCIA_MS=2000` (config de HU-03) |
| Modo simulado sin pesos | `backend/app/services/ia_yolo.py` | Si no existe `RUTA_MODELO`, genera clasificación ponderada (Orgánico 45 %, Inorgánico 35 %, Peligroso 20 %) y lo registra en el log |

### Avisos sobre la implementación

- **Preprocesamiento:** el código **no** hace `resize` ni normalización explícitos; solo convierte a RGB y delega el preprocesamiento en `YOLO.predict()`. No se modificó.
- **Límite de 2 s:** `TIEMPO_MAX_INFERENCIA_MS=2000` existe en la configuración, pero `ia_yolo.py` **no aborta** la inferencia si se supera; solo mide el tiempo y lo devuelve.
- **Pesos del modelo:** **no existe ningún `.pt`/`.onnx` en el proyecto**, solo el marcador `backend/app/ml/pesos/.gitkeep` (71 bytes). Por tanto **no hay ningún archivo de modelo mayor a 50 MB** que avisar/copiar. Sin pesos, el backend opera en modo simulado.
- **Enlace roto:** `backend/app/ml/README.md` referencia `docs/entrenamiento_yolo.md`, que no existe en la app completa.

## Archivos copiados

| Archivo | Tipo | Origen |
| --- | --- | --- |
| `backend/app/services/ia_yolo.py` | HU-04 | `RESIDATA completo/backend/app/services/ia_yolo.py` |
| `backend/app/ml/README.md` | HU-04 | `RESIDATA completo/backend/app/ml/README.md` |
| `backend/app/ml/__init__.py` | HU-04 | `RESIDATA completo/backend/app/ml/__init__.py` |
| `backend/app/ml/pesos/.gitkeep` | HU-04 | `RESIDATA completo/backend/app/ml/pesos/.gitkeep` |
| `backend/requirements-ml.txt` | Base (dependencias de IA) | `RESIDATA completo/backend/requirements-ml.txt` |

**Total: 5 archivos**, todos verificados byte a byte contra el origen.

### Archivo de modelo

| Archivo | Tamaño | ¿Copiado? |
| --- | --- | --- |
| `backend/app/ml/pesos/residuos_yolo.pt` | — | **No existe** en la app completa |

No se copió ningún peso porque el proyecto no los incluye (están excluidos por `.gitignore`:
`app/ml/pesos/*.pt` y `*.onnx`). No se superó el umbral de 50 MB en ningún caso.

## Dependencias de otras HU

- **HU-03 (obligatoria):**
  - `backend/app/core/config.py` — `obtener_configuracion()` y `ruta_modelo` / `tiempo_max_inferencia_ms`.
  - `backend/app/core/logging.py` — `obtener_logger()`.
- **HU-05 (consumidor):** `backend/app/services/procesamiento.py` invoca `ia_yolo.clasificar()` y aplica el umbral de confianza y la regla categoría → ángulo.
- **Nota:** HU-04 **no arranca aislada**; requiere la base de HU-03.

## Notas

- **Modo simulado por defecto:** al no haber pesos, toda inferencia será simulada hasta que se coloque `residuos_yolo.pt` en `backend/app/ml/pesos/`.
- **Dependencias opcionales:** `requirements-ml.txt` (`ultralytics`, `opencv-python`) solo se instala para inferencia real; arrastra PyTorch.
- **Sin Git:** esta entrega se creó solo con copia de archivos; no se ejecutó ningún comando de Git.
- El código se copió **sin modificaciones**; no se refactorizó ni se reformateó nada.
