# 📡 Firmware del Nodo IoT - ResiData

Este directorio contiene el código fuente C++ / Arduino para los nodos clasificadores basados en **ESP32-CAM (AI-Thinker)** y servomotores **SG90**.

---

## 📖 Documentación para Implementadores

Si vas a armar el hardware o flashear la placa, consulta la guía paso a paso completa:

👉 **[GUIA_IMPLEMENTACION.md](./GUIA_IMPLEMENTACION.md)**

Allí encontrarás:
1. Lista de componentes y materiales.
2. Esquema y tabla de cableado (pines GPIO, alimentación externa de 5V y GND común).
3. Configuración obligatoria en Arduino IDE 2.x (PSRAM, Huge APP, particionado).
4. Plantilla de credenciales `secrets.h` para conectarse al backend en Oracle Cloud (`150.136.142.202`).
5. Comandos de prueba interactivos por Monitor Serie (`t`, `s90`, `c`).
6. Guía de solución de problemas (Brownout, errores de cámara `0x105`, WiFi, etc.).

---

## 📂 Estructura del Código

```text
firmware/residata_nodo/
├── residata_nodo.ino     # Máquina de estados, loop principal, interrupción del sensor y watchdog
├── config.h              # Definición de pines GPIO, timers PWM, resoluciones y constantes
├── secrets.h.example     # Plantilla de credenciales WiFi, API Key y host del servidor
├── secrets.h             # Credenciales locales (ignorado en git)
├── camara.h / .cpp       # Controlador del sensor OV2640 y captura JPEG con PSRAM
├── red.h / .cpp          # Conexión WiFi y cliente HTTP multipart/form-data
├── servo_ctrl.h / .cpp   # Control PWM del servomotor SG90 mediante timers LEDC 2 y 3
└── sensor.h / .cpp       # Detección de presencia con sensor infrarrojo y botón manual
```
