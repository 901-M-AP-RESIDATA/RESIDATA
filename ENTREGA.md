# HU-06 — Accionamiento Físico del Servomotor (SG90)

- **ID:** HU-06
- **Nombre:** Accionamiento Físico del Servomotor (SG90)
- **Responsable:** Roberto
- **Prioridad:** Alta
- **Carpeta:** `HU-06_Servomotor-SG90`
- **Origen:** `RESIDATA completo` (copia íntegra, sin modificar el código)

## Tareas técnicas cubiertas

| Tarea técnica | Archivo(s) | Detalle |
| --- | --- | --- |
| Librería PWM (ESP32Servo) configurada | `firmware/residata_nodo/servo_ctrl.cpp`, `servo_ctrl.h` | `#include <ESP32Servo.h>`; reserva previa de timers LEDC 2 y 3 con `ESP32PWM::allocateTimer()` para no chocar con el XCLK de la cámara (timer 0) |
| Señal PWM hacia el ángulo recibido | `firmware/residata_nodo/servo_ctrl.cpp` | `setPeriodHertz(50)`, `attach(PIN_SERVO, 500, 2400)`; `servoMover(angulo)` limita a `[0, 180]` y aplica `sg90.write()` |
| Temporización no bloqueante de 3 segundos | `firmware/residata_nodo/residata_nodo.ino` (HU-01), `config.h` (HU-01) | Estado `ESPERA_CAIDA` compara `millis() - etapaDesdeMs >= TIEMPO_ESPERA_CAIDA_MS` (3000 ms) sin `delay()` |
| Retorno a la posición de reposo (90°) | `firmware/residata_nodo/servo_ctrl.cpp`, `config.h` (HU-01), `residata_nodo.ino` (HU-01) | `servoIniciar()` deja el servo en `SERVO_ANGULO_REPOSO` (90°); el estado `REGRESANDO` llama `servoMover(SERVO_ANGULO_REPOSO)` |

### Constantes asociadas (en `config.h`, entregado en HU-01)

| Constante | Valor | Uso |
| --- | --- | --- |
| `PIN_SERVO` | 14 | Pin de señal PWM |
| `SERVO_FRECUENCIA_HZ` | 50 | Periodo de 20 ms |
| `SERVO_US_MINIMO` / `SERVO_US_MAXIMO` | 500 / 2400 µs | Ancho de pulso |
| `SERVO_ANGULO_REPOSO` | 90 | Posición de reposo |
| `SERVO_ACOMODAR_MS` | 700 | Espera tras volver a reposo |
| `SERVO_TIMER_LEDC_A` / `_B` | 2 / 3 | Timers LEDC reservados |
| `TIEMPO_ESPERA_CAIDA_MS` | 3000 | Temporización no bloqueante de 3 s |

## Archivos copiados

| Archivo | Tipo | Origen |
| --- | --- | --- |
| `firmware/residata_nodo/servo_ctrl.cpp` | HU-06 | `RESIDATA completo/firmware/residata_nodo/servo_ctrl.cpp` |
| `firmware/residata_nodo/servo_ctrl.h` | HU-06 | `RESIDATA completo/firmware/residata_nodo/servo_ctrl.h` |

**Total: 2 archivos**, ambos verificados byte a byte contra el origen.

## Dependencias de otras HU

| HU | Qué se reutiliza |
| --- | --- |
| **HU-01 (obligatoria)** | `firmware/residata_nodo/config.h` (`PIN_SERVO`, `SERVO_*`, `TIEMPO_ESPERA_CAIDA_MS`) y `firmware/residata_nodo/residata_nodo.ino` (estados `ACCIONANDO` → `ESPERA_CAIDA` → `REGRESANDO` y temporización con `millis()`). También `docs/cableado.md` y `docs/pruebas_hardware.md` (paso 4: conflicto de timers cámara/servo) |
| **HU-02 (para compilar)** | `firmware/residata_nodo/red.h`, incluido por `residata_nodo.ino` |

- **Consecuencia:** esta carpeta **no compila aislada**; el sketch completo requiere HU-01 y HU-02.
  Se documenta como dependencia, sin modificar código.

## Notas

- **Archivos compartidos:** la temporización no bloqueante de 3 s y el retorno a 90° viven en
  `residata_nodo.ino` y `config.h`, ya entregados completos en HU-01 (regla 7). Esta carpeta solo
  aporta el driver del servo.
- **Riesgo de hardware:** el propio código advierte que el conflicto de timers LEDC entre cámara y
  servo debe validarse en placa (paso 4 de `docs/pruebas_hardware.md`).
- **Estado:** los archivos llevan la cabecera `ESTADO: NO VERIFICADO EN HARDWARE`.
- **Sin credenciales:** esta entrega no contiene configuración ni secretos.
- **Sin Git:** esta entrega se creó solo con copia de archivos; no se ejecutó ningún comando de Git.
- El código se copió **sin modificaciones**; no se refactorizó ni se reformateó nada.
