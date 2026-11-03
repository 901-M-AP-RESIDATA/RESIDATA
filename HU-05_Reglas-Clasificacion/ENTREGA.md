# HU-05 — Lógica de Clasificación Mecánica (Reglas de Negocio)

- **ID:** HU-05
- **Nombre:** Lógica de Clasificación Mecánica (Reglas de Negocio)
- **Responsable:** Juan Carlos
- **Prioridad:** Alta
- **Carpeta:** `HU-05_Reglas-Clasificacion`
- **Origen:** `RESIDATA completo` (copia íntegra, sin modificar el código)

## Tareas técnicas cubiertas

| Tarea técnica | Archivo(s) | Detalle |
| --- | --- | --- |
| Mapeo categoría → ángulo del servomotor (Orgánico 0°, Inorgánico 90°, Peligroso 180°) | `backend/app/services/procesamiento.py` | `_obtener_angulo()` consulta la tabla `reglas_servo` por `categoria_id`; los valores 0/90/180 se siembran en `database/02_datos_iniciales.sql` (HU-07) |
| Lógica fallback de posición por defecto con baja confianza de la IA | `backend/app/services/procesamiento.py` | Si `resultado.confianza < config.umbral_confianza` (0.60), se usa `config.categoria_baja_confianza` (`Peligroso`); `_obtener_angulo()` cae a la regla `es_por_defecto = TRUE` (Peligroso → 180°) y, si no existe, a 0° |
| Respuesta HTTP 200 con JSON hacia el ESP32-CAM | `backend/app/services/procesamiento.py` | Devuelve `RespuestaClasificacion` (categoría, `color_bolsa`, `angulo`, `confianza`, `tiempo_inferencia_ms`, `alerta_generada`, histórico); FastAPI lo serializa como JSON con código 200 en `POST /api/v1/dispositivo/clasificar` |

### Flujo implementado en `procesar_lectura()`

1. Ejecuta la inferencia (`ia_yolo.clasificar`).
2. Compara la confianza con `umbral_confianza` (0.60) y aplica el **fallback** a `Peligroso` si es baja.
3. Resuelve la categoría en el catálogo y su ángulo en `reglas_servo`.
4. Guarda la imagen, persiste el histórico y actualiza `ultima_conexion` del contenedor.
5. Genera alertas (`residuo_peligroso` si nivel ≥ 3, `baja_confianza` si aplica) y las difunde por WebSocket.
6. Retorna `RespuestaClasificacion` → JSON 200.

### Avisos

- **El mapeo 0/90/180 no está codificado en `procesamiento.py`**: se lee de la base de datos
  (`reglas_servo`), sembrada por `database/02_datos_iniciales.sql`. Por eso esta HU **depende de
  HU-07** para que el mapeo exista realmente.
- `procesamiento.py` es el **único archivo exclusivo** de esta HU según el mapa. Las reglas también
  viven en archivos ya entregados o posteriores: `core/config.py` (umbral y categoría de fallback,
  HU-03), `db/modelos.py` (`ReglaServo`, HU-07), `schemas/dispositivo.py` (contrato de respuesta,
  HU-03) y `database/02_datos_iniciales.sql` (HU-07).

## Archivos copiados

| Archivo | Tipo | Origen |
| --- | --- | --- |
| `backend/app/services/procesamiento.py` | HU-05 (compartido con HU-03/07/08/09) | `RESIDATA completo/backend/app/services/procesamiento.py` |

**Total: 1 archivo**, verificado byte a byte contra el origen.

## Dependencias de otras HU

| HU | Qué se reutiliza |
| --- | --- |
| **HU-03** | `core/config.py` (`umbral_confianza`, `categoria_baja_confianza`), `core/excepciones.py`, `core/logging.py`, `schemas/dispositivo.py`, `schemas/historico.py`, `services/almacenamiento.py` |
| **HU-04** | `services/ia_yolo.py` (`clasificar()`) |
| **HU-07** | `db/modelos.py` (`CategoriaResiduo`, `ReglaServo`, `HistoricoClasificacion`, `Alerta`, `Contenedor`) y `database/02_datos_iniciales.sql` (ángulos 0/90/180 y regla por defecto) |
| **HU-08** | `services/tiempo_real.py` (`gestor.difundir()`) |
| **HU-09** | `schemas/alerta.py` (`AlertaLeer`) |

- **Consecuencia:** esta carpeta **no es ejecutable de forma aislada**; es el orquestador que une las
  piezas de las demás HU. Se documenta como dependencia, sin modificar código.

## Notas

- **Sin credenciales:** esta entrega no contiene configuración ni secretos.
- **Respuesta 200:** el código de estado lo aporta FastAPI al serializar el `response_model` del
  endpoint de HU-03; `procesamiento.py` construye el objeto de respuesta.
- **Sin Git:** esta entrega se creó solo con copia de archivos; no se ejecutó ningún comando de Git.
- El código se copió **sin modificaciones**; no se refactorizó ni se reformateó nada.
