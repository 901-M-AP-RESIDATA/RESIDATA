# HU-01 — Captura de Imagen en el Borde

- **ID:** HU-01
- **Nombre:** Captura de Imagen en el Borde
- **Responsable:** Jose M.
- **Prioridad:** Alta
- **Carpeta:** `HU-01_Captura-Imagen-Borde`
- **Origen:** `RESIDATA completo` (copia íntegra, sin modificar el código)

## Tareas técnicas cubiertas

| Tarea técnica | Archivo(s) | Detalle |
| --- | --- | --- |
| Sensor de proximidad con interrupción por hardware | `firmware/residata_nodo/sensor.cpp`, `sensor.h` | `attachInterrupt()` sobre flanco `FALLING`; ISR `IRAM_ATTR onDisparoIr()`; bandera volátil de disparo |
| Cámara con resolución y calidad JPEG configuradas | `firmware/residata_nodo/config.h`, `camara.cpp` | OV2640 en `FRAMESIZE_SVGA` (800×600) y `CAM_JPEG_QUALITY 12`; inicialización y captura en `camara.cpp` |
| Debounce y disparo de captura al detectar un residuo | `firmware/residata_nodo/sensor.cpp`, `residata_nodo.ino` | Debounce de 150 ms en el sensor IR y 100 ms en el botón manual; transición `REPOSO → CAPTURANDO` en la máquina de estados |
| Gestión de memoria para guardar la imagen temporalmente | `firmware/residata_nodo/residata_nodo.ino`, `camara.cpp`, `camara.h` | Buffer `camera_fb_t *fbEnCurso` en PSRAM y liberación con `camaraLiberarBuffer()` |
| Latencia del ciclo de captura menor a 1 segundo | `firmware/residata_nodo/config.h`, `camara.cpp` | `CAM_GRAB_MODE CAMERA_GRAB_LATEST`, `fb_count = 2`, `CAM_FLASH_ESTABILIZAR_MS 80` |

## Archivos copiados

| Archivo | Tipo | Origen |
| --- | --- | --- |
| `README.md` | Base del proyecto | `RESIDATA completo/README.md` |
| `firmware/residata_nodo/.gitignore` | Base del proyecto | `RESIDATA completo/firmware/residata_nodo/.gitignore` |
| `firmware/residata_nodo/residata_nodo.ino` | HU-01 (compartido con HU-02, HU-05, HU-06) | `RESIDATA completo/firmware/residata_nodo/residata_nodo.ino` |
| `firmware/residata_nodo/config.h` | HU-01 (compartido con HU-02, HU-05, HU-06) | `RESIDATA completo/firmware/residata_nodo/config.h` |
| `firmware/residata_nodo/camara.cpp` | HU-01 | `RESIDATA completo/firmware/residata_nodo/camara.cpp` |
| `firmware/residata_nodo/camara.h` | HU-01 | `RESIDATA completo/firmware/residata_nodo/camara.h` |
| `firmware/residata_nodo/sensor.cpp` | HU-01 | `RESIDATA completo/firmware/residata_nodo/sensor.cpp` |
| `firmware/residata_nodo/sensor.h` | HU-01 | `RESIDATA completo/firmware/residata_nodo/sensor.h` |
| `docs/cableado.md` | HU-01 (compartido con HU-06) | `RESIDATA completo/docs/cableado.md` |
| `docs/pruebas_hardware.md` | HU-01 (compartido con HU-02, HU-06) | `RESIDATA completo/docs/pruebas_hardware.md` |

**Total: 10 archivos** (8 de la HU + 2 de Base del proyecto), todos verificados byte a byte contra el origen.

## Dependencias de otras HU

- **Ninguna previa.** HU-01 es la primera entrega del proyecto.
- **Dependencias hacia adelante** (esta entrega las necesita para compilar, pero se entregan después):
  - **HU-02:** `firmware/residata_nodo/red.h` — incluido por `residata_nodo.ino`.
  - **HU-06:** `firmware/residata_nodo/servo_ctrl.h` — incluido por `residata_nodo.ino`.

## Notas

- **Archivos compartidos:** `config.h`, `residata_nodo.ino`, `docs/cableado.md` y `docs/pruebas_hardware.md` sirven a varias HU; se copian completos aquí (regla 7) y las HU posteriores los referencian como dependencia.
- **Compilación parcial:** el sketch `residata_nodo.ino` no compila de forma aislada hasta contar con HU-02 y HU-06, por los `#include` de `red.h` y `servo_ctrl.h`.
- **Credenciales:** `firmware/residata_nodo/secrets.h` **no se copia** (está en `.gitignore` y es configuración local). Su plantilla `secrets.h.example` se entregará en HU-02. Se verificó que no contiene credenciales reales.
- **Sin Git:** esta entrega se creó solo con copia de archivos; no se ejecutó ningún comando de Git.
- El código se copió **sin modificaciones**; no se refactorizó ni se reformateó nada.
