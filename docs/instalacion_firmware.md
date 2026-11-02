# ResiData - Instalación del Firmware del Nodo IoT

Guía para compilar y cargar el firmware `residata_nodo` en una
**ESP32-CAM AI-Thinker** con Arduino IDE.

> **ADVERTENCIA IMPORTANTE**
> Todos los módulos del firmware llevan la cabecera
> `ESTADO: NO VERIFICADO EN HARDWARE` y **no se ha podido compilar ni
> ejecutar en hardware en la máquina de desarrollo**. Valide usted mismo la
> compilación en Arduino IDE y siga paso a paso la lista de verificación de
> `docs/pruebas_hardware.md` antes de poner el nodo en producción.

---

## 1. Requisitos

- **Arduino IDE** 2.x.
- Paquete de placas **esp32 de Espressif**.
- Librerías: **ESP32Servo**, **ArduinoJson (v7)**.
  (`esp_camera`, `WiFi` y `esp_task_wdt` vienen incluidas en el paquete esp32.)

### 1.1 Instalar el paquete de placas esp32

1. Abra **Archivo → Preferencias** y añada en
   *"URLs adicionales de Gestor de placas"*:

   ```
   https://espressif.github.io/arduino-esp32/package_esp32_index.json
   ```

2. **Herramientas → Placa → Gestor de placas**, busque `esp32` e instale
   **esp32 by Espressif Systems** (la versión más reciente estable).

### 1.2 Instalar las librerías

- **Gestor de librerías** (`Herramientas → Gestión de librerías`):
  - `ESP32Servo` (autor: Kevin Harrington).
  - `ArduinoJson` (autor: Benoit Blanchon) versión **7.x**.

---

## 2. Configuración de la placa

Con el proyecto abierto, en **Herramientas**:

| Opción | Valor |
| --- | --- |
| Placa | **AI Thinker ESP32-CAM** |
| Partition Scheme | **Huge APP (3MB No OTA/1MB SPIFFS)** |
| PSRAM | **Habilitada** |
| Flash Mode | QIO (por defecto) |
| Flash Size | 4MB |
| Velocidad de carga | **115200** |
| Puerto | el de la base CH340/FTDI |

> La cámara necesita PSRAM para usar `fb_count = 2` (doble buffer). Con
> PSRAM deshabilitada el firmware falla al inicializar.

---

## 3. Estructura del proyecto

```
firmware/residata_nodo/
├── residata_nodo.ino     (máquina de estados, LED, watchdog, modo prueba)
├── config.h              (pines, resoluciones, tiempos, reintentos)
├── secrets.h.example     (plantilla de credenciales)
├── secrets.h             (creado LOCALMENTE, NO versionado)
├── camara.h / camara.cpp
├── red.h / red.cpp
├── servo_ctrl.h / servo_ctrl.cpp
└── sensor.h / sensor.cpp
```

Abra el archivo `residata_nodo.ino`; Arduino IDE cargará el resto de
archivos de la carpeta automáticamente.

---

## 4. Configurar credenciales (`secrets.h`)

1. Copie la plantilla:

   ```bash
   cp secrets.h.example secrets.h
   ```

2. Rellene los valores (nunca commitee `secrets.h`; está excluido en el
   `.gitignore` del proyecto):

   | Definición | Valor |
   | --- | --- |
   | `WIFI_SSID` / `WIFI_PASS` | Credenciales del WiFi **2.4 GHz** local |
   | `SERVER_HOST` | **IP de la PC** donde corre el backend FastAPI |
   | `SERVER_PORT` | `8000` (puerto del backend) |
   | `CONTENEDOR_ID` | Identificador del contenedor en ResiData |
   | `API_KEY` | API key del contenedor (columna `api_key` de la BD) |

   > Si el backend y el nodo están en redes/subredes distintas, el contrato
   > HTTP de `redEnviarCaptura()` no funcionará. Ambos deben estar en la
   > misma LAN.

**Endpoints usados por el firmware**

- `POST http://SERVER_HOST:SERVER_PORT/api/v1/dispositivo/clasificar`
  - Cabecera: `X-API-Key: <API_KEY>`
  - `multipart/form-data` con campo `contenedor_id` (texto) y `imagen`
    (archivo `captura.jpg`, `image/jpeg`).
  - Respuesta `200`: `{"angulo": 90, "categoria": "Inorgánico", "confianza": 0.93}`
  - Errores: `400` (imagen inválida), `401` (API key), `404` (contenedor).

---

## 5. Carga del firmware

### 5.1 Con base ESP32-CAM-MB (CH340)

1. Coloque la placa en la base y conecte el USB a la PC.
2. En Arduino IDE, Verificar (✓) y **Cargar**. La base gestiona los pines
   DTR/RTS automáticamente (no requiere pulsar botones).
3. Tras la carga, abra el **Monitor Serie a 115200**.

### 5.2 Con adaptador FTDI

1. Conecte: `FTDI TX → ESP32 RX (GPIO 3)`, `FTDI RX → ESP32 TX (GPIO 1)`,
   `3V3`, `GND`.
2. **Conecte GPIO 0 a GND** (modo programación) **antes de energizar**.
3. Cargue el firmware.
4. **Retire el puente de GPIO 0 a GND** y **reinicie** la placa (EN a GND y
   soltar, o desconectar/energizar).
5. Monitor Serie a 115200 para ver los logs.

---

## 6. Modo de prueba por Serial

Tras cargar y reiniciar, abra el monitor serie (115200 baudios) y espere a
que el estado pase a `REPOSO` (led rojo apagado). Comandos disponibles:

| Comando | Acción |
| --- | --- |
| `t` | Dispara un **ciclo completo** (captura → envío → servo) |
| `s90` (o `s0`, `s180`, …) | Mueve el servo al ángulo indicado |
| `c` | Captura una foto y reporta su tamaño en bytes |

Logs por módulo con prefijos `[CAM]`, `[RED]`, `[SERVO]`, `[SENSOR]`.

---

## 7. Comportamiento e indicadores

- **LED flash blanco (GPIO 4):** se enciende unos instantes durante la captura.
- **LED rojo (GPIO 33):**
  - Parpadeo **lento** = conectando WiFi.
  - **Encendido fijo** = procesando (captura/envío/servo).
  - **3 parpadeos rápidos** = error de envío.
- **Watchdog:** se alimenta en cada iteración del `loop`; si algo bloquea el
  ciclo más de `WDT_TIMEOUT_SEGUNDOS`, reinicia la placa.
- **Reinicio controlado:** tras `MAX_FALLOS_CONSECUTIVOS` errores seguidos
  el nodo se reinicia solo.

---

## 8. Solución de problemas

| Síntoma | Causa probable | Solución |
| --- | --- | --- |
| `Brownout detector was triggered` al arrancar | Fuente insuficiente o picos del servo | Fuente 5 V/2 A, capacitor 470–1000 µF cerca del servo, GND común |
| `Camera init failed 0x105` | PSRAM deshabilitada, pines equivocados o alimentación débil | Habilitar PSRAM; revisar `config.h` (pines AI-Thinker); fuente externa |
| El servo tiembla o reinicia la placa | Alimentación desde 3V3 o picos de corriente | Servo a 5 V de la fuente externa + capacitor; nunca 3V3 |
| WiFi no conecta | El ESP32-CAM solo soporta **2.4 GHz** | Usar red 2.4 GHz; verificar SSID/contraseña y alcance/antena |
| Respuesta `401` | API key incorrecta o contenedor inexistente | Revisar `API_KEY` y que el contenedor exista en la BD |
| Respuesta `404` | No existe el contenedor en el backend | Revisar `api_key`/contenedor en la BD |
| Respuesta `400` | Imagen inválida (vacía o corrompida) | Revisar captura con `c`; calidad JPEG |
| El nodo se reinicia en bucle | Fallos consecutivos (`MAX_FALLOS_CONSECUTIVOS`) | Ver logs por Serial; corregir causa antes de que cuente 3 fallos |

---

## 9. Notas de diseño

- **Orden de inicialización:** `camaraIniciar()` es la PRIMERA acción del
  `setup()` (reserva el timer LEDC 0/canal 0 para XCLK). Después
  `servoIniciar()` reserva los **timers LEDC 2 y 3** con
  `ESP32PWM::allocateTimer()` y hace `attach` a 50 Hz con pulsos
  500–2400 µs. Nunca se comparte el timer 0 con el servo.
- **Multipart manual:** `HTTPClient` no genera multipart nativo; el cuerpo se
  construye byte a byte (cabeceras + preámbulo + JPEG + cierre) y se valida el
  `Content-Length`. Reintentos: 3 con backoff 500 ms / 1 s / 2 s.
- **Objetivo de captura:** < 1 s desde la activación (sensor/ISR) hasta tener
  la imagen: debounce 150 ms + flash 80 ms + `esp_camera_fb_get()`.