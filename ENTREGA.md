# HU-02 — Transmisión de Imagen al Servidor (API)

- **ID:** HU-02
- **Nombre:** Transmisión de Imagen al Servidor (API)
- **Responsable:** Victor
- **Prioridad:** Alta
- **Carpeta:** `HU-02_Transmision-Imagen-API`
- **Origen:** `RESIDATA completo` (copia íntegra, sin modificar el código)

## Tareas técnicas cubiertas

| Tarea técnica | Archivo(s) | Detalle |
| --- | --- | --- |
| Cliente Wi-Fi en ESP32 | `firmware/residata_nodo/red.cpp`, `red.h` | `WiFi.mode(WIFI_STA)`, `setSleep(false)`, `setAutoReconnect(true)`; `redIniciar()`, `redConectada()` y `redReconectarSiCaida()` |
| Cliente HTTP en C++ que envía la imagen y el ID de contenedor | `firmware/residata_nodo/red.cpp` | Petición `POST /api/v1/dispositivo/clasificar` construida a mano con `WiFiClient`: multipart con campo `imagen` (`captura.jpg`) y campo `contenedor_id`, más cabecera `X-API-Key` |
| Reintentos (máx. 3) con backoff exponencial | `firmware/residata_nodo/red.cpp`, `config.h` (HU-01) | Bucle `intento <= RED_MAX_REINTENTOS` (3); esperas `RED_BACKOFF_MS = {500, 1000, 2000}` ms |
| Timeouts en el socket HTTP | `firmware/residata_nodo/red.cpp`, `config.h` (HU-01) | Conexión TCP con `RED_TIMEOUT_CONEXION_MS` (5 s) y lectura con deadline `RED_TIMEOUT_LECTURA_MS` (8 s) |
| Validación del código HTTP 200 | `firmware/residata_nodo/red.cpp` | Se extrae el código de la primera línea HTTP y solo hay éxito si `codigoHttp == 200`; después valida el JSON (`angulo` en [0, 180]) |

## Archivos copiados

| Archivo | Tipo | Origen |
| --- | --- | --- |
| `firmware/residata_nodo/red.cpp` | HU-02 | `RESIDATA completo/firmware/residata_nodo/red.cpp` |
| `firmware/residata_nodo/red.h` | HU-02 (compartido con HU-05) | `RESIDATA completo/firmware/residata_nodo/red.h` |
| `firmware/residata_nodo/secrets.h.example` | HU-02 (compartido con HU-01) | `RESIDATA completo/firmware/residata_nodo/secrets.h.example` |
| `docs/instalacion_firmware.md` | HU-02 | `RESIDATA completo/docs/instalacion_firmware.md` |

**Total: 4 archivos**, todos verificados byte a byte contra el origen.

## Dependencias de otras HU

- **HU-01 (obligatoria):**
  - `firmware/residata_nodo/config.h` — constantes usadas por `red.cpp`: `RED_MAX_REINTENTOS`, `RED_BACKOFF_MS`, `RED_TIMEOUT_CONEXION_MS`, `RED_TIMEOUT_LECTURA_MS`, `WIFI_RECONEXION_ESPERA_MS`, `NOMBRE_NODO`, `VERSION_FIRMWARE`.
  - `firmware/residata_nodo/residata_nodo.ino` — llama a `redIniciar()`, `redConectada()`, `redReconectarSiCaida()` y `redEnviarCaptura()` dentro de la máquina de estados.
  - `firmware/residata_nodo/camara.*` — proporciona el buffer JPEG que se envía.
  - `docs/pruebas_hardware.md` — checklist donde se valida el contrato HTTP (paso 6).
- **HU-06 (para compilar):** `firmware/residata_nodo/servo_ctrl.h`, incluido por `residata_nodo.ino`.

## Notas

- **Archivo compartido:** `red.h` define `RespuestaClasificacion`, reutilizado por HU-05. Se copia completo aquí y HU-05 lo referenciará como dependencia.
- **Credenciales:** solo se copia `secrets.h.example`, con **placeholders** (`MI_RED_WIFI`, `mi_contrasena`, `192.168.1.100`, `cambia_esta_clave`). El archivo real `secrets.h` **no se copia** (configuración local ignorada). No hay credenciales reales en esta entrega.
- **Estado del código:** los archivos llevan la cabecera `ESTADO: NO VERIFICADO EN HARDWARE`; el propio código advierte que el contrato multipart debe validarse contra el backend.
- **Detalle del contrato:** el backend autentica por `X-API-Key`; el campo `contenedor_id` viaja como informativo.
- **Sin Git:** esta entrega se creó solo con copia de archivos; no se ejecutó ningún comando de Git.
- El código se copió **sin modificaciones**; no se refactorizó ni se reformateó nada.
