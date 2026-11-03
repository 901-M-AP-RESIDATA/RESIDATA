# ResiData - Lista de Verificación de Hardware (Nodo IoT)

Pruebas ordenadas para validar el firmware `residata_nodo` **cuando se
disponga del hardware físico**. El firmware está marcado
`ESTADO: NO VERIFICADO EN HARDWARE`, así que estas pruebas son obligatorias
antes de dar el nodo por operativo.

> Reglas antes de empezar:
> - Alimentación externa 5 V / 2 A y capacitor 470–1000 µF cerca del servo.
> - Cargar el firmware según `docs/instalacion_firmware.md`.
> - Monitor Serie a 115200 para ver logs `[CAM]`, `[RED]`, `[SERVO]`, `[SENSOR]`.
> - Anotar el resultado (OK / FALLO) de cada paso. Reporte los fallos al
>   desarrollador del firmware con el log de consola completo.

---

## Paso 1. Alimentación y WiFi

**Procedimiento:** energizar la placa y observar el monitor serie.

- **Resultado esperado:** sin mensajes de brownout; el LED rojo parpadea
  lento (conectando) y luego se apaga; el log muestra
  `[RED] Conectada. IP: 192.168.x.x` y el estado pasa a `REPOSO`.
- **Si falla:**
  - `Brownout detector was triggered` → fuente insuficiente; subir a 5 V/2 A
    y comprobar el capacitor y el GND común.
  - WiFi que no conecta → verificar SSID/contraseña, red 2.4 GHz, posición
    de la antena; probar `WiFi.status()` en el log.

---

## Paso 2. Cámara sola (captura por Serial)

**Procedimiento:** con el nodo en `REPOSO`, enviar `c` por Serial.

- **Resultado esperado:** el flash enciende brevemente y el log muestra
  `[CAM] Frame capturado: NNNN bytes` y `[CMD] Foto OK, tamaño NNNN bytes
  (800x600)`. N debe estar típicamente entre 5 KB y 60 KB.
- **Qué revisar si falla:**
  - `Camera init failed 0x105` → PSRAM deshabilitada, pines equivocados en
    `config.h`, o alimentación débil. Habilitar PSRAM, revisar pines AI-Thinker.
  - Foto siempre `0` bytes o NULL → revisar lentes/cable plano de la cámara
    y `jpeg_quality`.

---

## Paso 3. Servo solo

**Procedimiento:** con el nodo en `REPOSO`, enviar `s0`, `s90`, `s180`.

- **Resultado esperado:** el servo se mueve suave y sin temblores a cada
  ángulo y se queda quieto a `90` tras el último comando de reposo.
- **Qué revisar si falla:**
  - Temblor o reinicio de la placa → el servo está alimentado desde 3V3 o
    falta el capacitor. Conectar el **5 V de la fuente externa** y añadir
    470–1000 µF.
  - No se mueve nada → revisar el pin `GPIO 14` y la señal (naranja).

---

## Paso 4. Cámara y servo JUNTOS (conflicto de timers — OBLIGATORIO)

**Procedimiento:** con el nodo en `REPOSO`, capturar con `c` y mover con
`s90` de forma intercalada y repetida durante al menos 1 minuto.

- **Resultado esperado:** la cámara sigue capturando frames correctamente
  MIENTRAS el servo se mueve. No debe degradarse la captura ni aparecer
  `0x105` en caliente.
- **Por qué se prueba:** la cámara usa el timer LEDC 0 / canal 0 para XCLK.
  El firmware reserva los timers 2 y 3 con `ESP32PWM::allocateTimer()` en
  `servoIniciar()`. Esta prueba confirma que no compiten.
- **Qué revisar si falla:**
  - Si al mover el servo la cámara deja de capturar (`esp_camera_fb_get()`
    NULL o `0x105`) → revisar el orden de inicialización en `setup()`
    (cámara PRIMERO) y que `SERVO_TIMER_LEDC_A/B` no colisionen con el 0.

---

## Paso 5. Sensor y botón

**Procedimiento:**
1. Acercar un objeto (o la mano) al sensor IR.
2. Pulsar el botón manual.

- **Resultado esperado:** cada detección genera
  `[SENSOR] Detección por sensor IR` y un ciclo completo; la pulsación del
  botón genera `[SENSOR] Disparo por botón manual` y otro ciclo. Los disparos
  durante un ciclo en curso se ignoran (`Ciclo en curso, disparo ignorado`).
- **Qué revisar si falla:**
  - FC-51 sin respuesta → nivel lógico invertido (ajustar potenciómetro de
    alcance o revisar si la salida es activa alta); el firmware espera
    FALLING.
  - Disparos repetidos/encendidos fantasma → ruido; revisar que el debounce
    (150 ms) se respeta y el cableado de GND.
  - E18-D80NK sin pull-up → verificar la resistencia de pull-up a 3.3 V
    (nunca 5 V al GPIO).

---

## Paso 6. Envío al servidor (backend FastAPI)

**Procedimiento:** asegurar que el backend corre en la PC (misma red local)
y que `SERVER_HOST`/`API_KEY`/`CONTENEDOR_ID` en `secrets.h` son correctos.
Enviar `t` (ciclo completo) o `c` + envío.

- **Resultado esperado:** el log muestra
  `[RED] Enviando NNNN bytes`, luego `[RED] Respuesta OK: angulo=NN categoria=...`
  y el servo se mueve al ángulo recibido. El backend registra la clasificación
  (panel web: "Últimas clasificaciones" y contadores).
- **Qué revisar si falla:**
  - `401` → API key incorrecta o contenedor inexistente.
  - `404` → contenedor no encontrado en la BD.
  - `400` → imagen inválida (revisar la captura).
  - Sin respuesta/timeout → IP/puerto del backend, firewall de Windows, o
    backend no arrancado. Probar primero con el navegador: `http://IP:8000/docs`.
  - WiFi caída entre intentos → el firmware reconecta solo; verifique logs.

---

## Paso 7. Ciclo completo end-to-end

**Procedimiento:** colocar un residuo sobre el sensor (o pulsar el botón) y
dejar el ciclo natural completo.

- **Resultado esperado:**
  1. `[SENSOR] Disparo validado...`
  2. Flash → `[CAM] Frame capturado: NNNN bytes`
  3. `[RED] Enviando...` → `[RED] Respuesta OK` (backend responde 200)
  4. `[SERVO] Moviendo a NN grados` (ángulo del backend)
  5. Espera de 3 s → `[SERVO] Regresando a reposo (90)`
  6. LED rojo: encendido fijo durante el proceso y apagado en reposo.
- **Qué revisar si falla:**
  - El ciclo dura más de ~1 s capturando → revisar `CAM_FB_COUNT`/PSRAM y
    `CAM_GRAB_MODE`.
  - El residuo no cae → revisar la geometría de la rampa y el ángulo
    devuelto por el backend; aumentar `TIEMPO_ESPERA_CAIDA_MS` si la ruleta
    necesita más tiempo.

---

## Paso 8. Robustez (opcional)

- **Fallos encadenados:** apagar el backend y disparar 3 veces seguidas.
  El nodo debe mostrar 3 parpadeos rápidos y reiniciarse solo
  (`Reinicio controlado`).
- **Watchdog:** bloquear manualmente el ciclo (por ejemplo, desconectando el
  WiFi durante el envío) y comprobar que el WDT (20 s) reinicia la placa si
  algo se cuelga.
- **Ciclos continuos:** dejar 50+ ciclos seguidos sin pérdidas de buffer
  ni reinicios.

---

Al completar todos los pasos con resultado OK, el nodo se considera operativo
y se debe **retirar la marca `ESTADO: NO VERIFICADO EN HARDWARE`** de los
módulos y de la documentación.