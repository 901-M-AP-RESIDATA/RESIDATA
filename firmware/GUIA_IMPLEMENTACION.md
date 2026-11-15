# 🛠️ Guía de Implementación del Nodo IoT (ESP32-CAM) — ResiData

Esta guía está diseñada paso a paso para la persona encargada de ensamblar el hardware, conectar los componentes, configurar el entorno en Arduino IDE, compilar y cargar el firmware en la placa **ESP32-CAM**.

---

## 📋 1. Lista de Materiales Necesarios

| Componente | Especificación / Modelo | Propósito |
| :--- | :--- | :--- |
| **Microcontrolador** | ESP32-CAM AI-Thinker (con cámara OV2640) | Procesamiento, cámara y conexión WiFi |
| **Base de programación** | ESP32-CAM-MB (micro-USB con chip CH340) o módulo FTDI | Carga de firmware y depuración Serial |
| **Actuador mecánico** | Servomotor SG90 (9g) | Mover la compuerta de clasificación (0°, 90°, 180°) |
| **Sensor de presencia** | Sensor infrarrojo FC-51 o sensor fotoeléctrico E18-D80NK | Detectar cuándo cae un residuo |
| **Fuente de alimentación** | Fuente externa regulada de **5V / 2A a 3A** | Alimentación estable para ESP32 + Servo |
| **Capacitor** | Electrolítico de **470 µF a 1000 µF (16V)** | Filtrar caídas de tensión (evitar *brownout*) |
| **Botón pulsador** | Push button de 2 pines (opcional) | Disparo manual de captura |
| **Cables y protoboard** | Jumpers Dupont (macho-hembra y macho-macho) | Conexión de señales y alimentación |

---

## ⚡ 2. Diagrama y Tabla de Conexiones (Cableado)

> ⚠️ **REGLA DE ORO DE ALIMENTACIÓN:**
> 1. **NUNCA** alimentes el servomotor desde el pin `3V3` o `5V` del ESP32-CAM. El arranque del motor consume picos de hasta 800 mA que reinician la placa (*Brownout*).
> 2. El servomotor debe alimentarse **directamente desde la fuente externa de 5V**.
> 3. **GND COMÚN OBLIGATORIO:** Conecta la tierra (GND) de la fuente externa, del ESP32-CAM, del sensor y del servomotor juntas.
> 4. Coloca el **capacitor de 470–1000 µF** entre `+5V` y `GND` de la fuente lo más cerca posible del servomotor.

### Tabla de Pines:

| Componente | Cable / Pin del Componente | Conectar a (ESP32-CAM / Fuente) | Notas |
| :--- | :--- | :--- | :--- |
| **Servo SG90** | Cable Naranja (Señal PWM) | **GPIO 14** | Control de ángulo |
| **Servo SG90** | Cable Rojo (VCC) | **+5V de Fuente Externa** | ⚠️ NUNCA a 3.3V de la placa |
| **Servo SG90** | Cable Marrón (GND) | **GND Común** | Masa compartida |
| **Sensor IR FC-51**| Salida OUT / Digital | **GPIO 13** | Flanco de bajada (FALLING) |
| **Sensor IR FC-51**| VCC | **Pin 3V3** del ESP32-CAM | Opera a nivel lógico de 3.3V |
| **Sensor IR FC-51**| GND | **GND Común** | Masa compartida |
| **Botón Manual** | Terminal 1 | **GPIO 15** | Configurado como INPUT_PULLUP |
| **Botón Manual** | Terminal 2 | **GND Común** | Cierra a tierra al presionar |
| **ESP32-CAM** | Pin 5V | **+5V de Fuente Externa** | Alimentación de la placa |
| **ESP32-CAM** | Pin GND | **GND Común** | Masa compartida |

> 🚫 **PINES RESERVADOS (NO CONECTAR NADA AQUÍ):**
> - **GPIO 0:** Modo de programación y reloj XCLK de la cámara.
> - **GPIO 1 y 3:** Pines TX y RX de la comunicación serial (USB).
> - **GPIO 2 y 12:** Pines de arranque (*strapping*).
> - **GPIO 16:** Memoria PSRAM interna.
> - **GPIO 4 y 33:** LEDs integrados (Flash blanco en pin 4, LED rojo en pin 33).

---

## 💻 3. Configuración del Entorno en Arduino IDE

1. Descarga e instala **Arduino IDE 2.x** (desde [arduino.cc](https://www.arduino.cc/en/software)).
2. Abre **Archivo → Preferencias** (o `Ctrl + Coma`).
3. En el campo **URLs adicionales de Gestor de placas**, pega la siguiente URL:
   ```text
   https://espressif.github.io/arduino-esp32/package_esp32_index.json
   ```
4. Ve a **Herramientas → Placa → Gestor de placas**:
   * Busca: `esp32`
   * Instala: **esp32 by Espressif Systems** (versión 2.0.x o superior).
5. Ve a **Herramientas → Gestión de librerías** (`Ctrl + Shift + I`):
   * Busca e instala: **ESP32Servo** (por Kevin Harrington).
   * Busca e instala: **ArduinoJson** (por Benoit Blanchon) en su **versión 7.x**.

---

## ⚙️ 4. Opciones de Placa en Arduino IDE

Conecta el ESP32-CAM a tu computadora mediante la base USB (ESP32-CAM-MB) y configura el menú **Herramientas** exactamente con estos valores:

| Ajuste en Herramientas | Valor Obligatorio | Por qué es crítico |
| :--- | :--- | :--- |
| **Placa** | **AI Thinker ESP32-CAM** | Define el mapa de pines de la cámara OV2640 |
| **Partition Scheme** | **Huge APP (3MB No OTA/1MB SPIFFS)** | El código + librerías WiFi/JSON superan 1.3 MB |
| **PSRAM** | **Enabled** (Habilitada) | ⚠️ **Esencial:** sin PSRAM falla la captura de imagen |
| **Flash Mode** | **QIO** (o DIO) | Velocidad de lectura de memoria |
| **Flash Frequency** | **80MHz** | Rendimiento óptimo |
| **Upload Speed** | **115200** (o 921600 si tu cable es de calidad) | Velocidad de flasheo |
| **Puerto** | El puerto COM o `/dev/ttyUSB0` detectado | Puerto serial del convertidor CH340 |

---

## 🔑 5. Configuración de Credenciales (`secrets.h`)

1. Entra a la carpeta del proyecto en `firmware/residata_nodo/`.
2. Si no existe el archivo `secrets.h`, copia la plantilla:
   ```bash
   cp secrets.h.example secrets.h
   ```
3. Abre `secrets.h` y edita tus parámetros:

```cpp
#pragma once

// 1. Red WiFi (Solo redes 2.4 GHz; el ESP32 no soporta 5 GHz)
#define WIFI_SSID       "NOMBRE_DE_TU_WIFI"
#define WIFI_PASS       "CONTRASENA_DE_TU_WIFI"

// 2. Servidor Backend en la Nube (Oracle Cloud)
#define SERVER_HOST     "150.136.142.202"
#define SERVER_PORT     8080               // O puerto 80

// 3. Identificador del nodo y Clave de API
#define CONTENEDOR_ID   "1"
#define API_KEY         "cambia_esta_clave" // O la nueva clave generada
```

---

## 🚀 6. Compilación y Carga del Firmware

### Si utilizas la base ESP32-CAM-MB (Recomendado):
1. Inserta el ESP32-CAM en la base y conecta el cable micro-USB a la PC.
2. Abre el archivo `firmware/residata_nodo/residata_nodo.ino` en Arduino IDE.
3. Haz clic en el botón **Subir** (flecha hacia la derecha `➔`).
4. La base maneja automáticamente los estados de GPIO 0 y Reset.
5. Al finalizar verás: `Leaving... Hard resetting via RTS pin...`

### Si utilizas un módulo FTDI / USB-Serial manual:
1. Conecta: `FTDI TX` ➔ `ESP32 U0R (GPIO 3)`, `FTDI RX` ➔ `ESP32 U0T (GPIO 1)`, `GND` ➔ `GND`, `5V` ➔ `5V`.
2. **Une con un cable GPIO 0 a GND** (modo bootloader).
3. Presiona el botón físico de **RESET** en la placa.
4. Presiona **Subir** en Arduino IDE.
5. En cuanto termine la carga, **DESCONECTA el cable de GPIO 0 a GND**.
6. Presiona el botón de **RESET** para iniciar el firmware en modo normal.

---

## 🔍 7. Pruebas y Depuración por Monitor Serie

1. Abre el **Monitor Serie** en Arduino IDE (`Ctrl + Shift + M`).
2. Configura la velocidad a **115200 baudios**.
3. Presiona el botón **RESET** de la placa para ver el arranque:

### Salida esperada en Monitor Serie:
```text
[INIT] Iniciando ResiData Nodo IoT...
[CAM] Iniciando camara OV2640...
[CAM] Camara inicializada correctamente.
[SERVO] Inicializando SG90 en GPIO 14...
[SERVO] Posicion inicial a 0 grados.
[RED] Conectando a WiFi...
[RED] WiFi conectado. IP local: 192.168.1.75
[NODO] Sistema en modo REPOSO. Listo para capturar.
```

### Comandos interactivos disponibles por teclado:
Puedes escribir estos caracteres en la barra del Monitor Serie y presionar **Enter**:
* **`t`**: Ejecuta un ciclo de prueba completo (Toma foto ➔ Envía al servidor ➔ Recibe categoría de IA ➔ Mueve el servomotor).
* **`s0`**, **`s90`**, **`s180`**: Mueve manualmente el servomotor al ángulo especificado.
* **`c`**: Toma una foto de prueba y reporta el tamaño del JPEG en bytes.

---

## 🚦 8. Indicadores LED del Nodo

* **LED Flash blanco frontal (GPIO 4):**
  * Se enciende durante una fracción de segundo al momento de tomar la foto para iluminar el residuo.
* **LED rojo posterior (GPIO 33):**
  * **Parpadeo lento (1 seg):** Conectando a la red WiFi.
  * **Encendido fijo:** Procesando imagen y comunicándose con el servidor.
  * **3 parpadeos rápidos:** Error de comunicación con el backend (código HTTP 401, 404 o 500).
  * **Apagado:** Nodo en reposo esperando que caiga un residuo.

---

## 🎯 9. Ángulos del Servomotor y Clasificación

Cuando el backend responde con la inferencia de la red neuronal YOLOv8, el nodo actúa de la siguiente manera:

| Categoría Detectada por IA | Ángulo del Servo | Color de Bolsa Asignado |
| :--- | :---: | :--- |
| **Orgánico** | **0°** | 🟢 Verde (Comida, cáscaras, biodegradables) |
| **Inorgánico** | **90°** | 🔵 Azul (Botellas, plástico, latas, vidrio) |
| **Peligroso / Desconocido** | **180°** | 🔴 Rojo (Pilas, baterías, bajo umbral) |

---

## 🛠️ 10. Guía de Solución de Problemas (Troubleshooting)

| Error / Síntoma | Causa Frecuente | Solución |
| :--- | :--- | :--- |
| `Brownout detector was triggered` | Caída de voltaje por alimentar el servo desde el ESP32 o puerto USB débil. | Usar fuente de 5V/2A dedicada, colocar capacitor de 1000 µF entre 5V y GND cerca del motor, verificar GND común. |
| `Camera init failed with error 0x105` | PSRAM deshabilitada en Arduino IDE o cámara mal insertada. | Menú Herramientas ➔ **PSRAM: Enabled**. Revisa que el flex de la cámara esté bien ajustado en su conector. |
| El motor hace ruido o vibra pero no gira | Voltaje insuficiente o cables invertidos. | Revisa que VCC sea 5V externo y que el cable naranja esté en GPIO 14. |
| Respuesta HTTP `401 Unauthorized` | La API Key en `secrets.h` no coincide con la registrada en la base de datos. | Revisa la directiva `API_KEY` en `secrets.h` (por defecto `cambia_esta_clave` o la regenerada en el panel). |
| Error `WiFi connection failed` | Red de 5 GHz seleccionada o contraseña incorrecta. | El ESP32 solo soporta redes **2.4 GHz**. Conéctalo a una banda 2.4 GHz. |
| El sensor IR se activa solo o no detecta | Sensibilidad descalibrada. | Gira el potenciómetro azul del sensor FC-51 con un desarmador plano pequeño hasta que el LED indicador solo encienda al acercar un objeto a 5-10 cm. |
