/*
 * ResiData - Nodo IoT (ESP32-CAM AI-Thinker)
 * residata_nodo.ino: maquina de estados principal, indicadores por LED,
 * watchdog y modo de prueba por Serial.
 *
 * FLUJO DE ESTADOS (no bloqueante, basado en millis()):
 *
 *   INICIO -> REPOSO -> CAPTURANDO -> ENVIANDO -> ACCIONANDO
 *                    -> ESPERA_CAIDA -> REGRESANDO -> REPOSO
 *                    (y ERROR con recuperacion)
 *
 * SALIDAS / PRECONDICIONES:
 *   - La camara debe inicializarse ANTES que el servo (el servo reserva
 *     los timers LEDC 2 y 3; la camara usa el timer 0). Orden en setup().
 *   - El flujo es no bloqueante salvo en CAPTURANDO (captura de frame) y
 *     ENVIANDO (envio HTTP con reintentos); el watchdog cubre ambos.
 *
 * ESTADO: NO VERIFICADO EN HARDWARE
 *  - Flujo completo pendiente de validacion (paso 7 de
 *    docs/pruebas_hardware.md).
 */

#include "config.h"
#include "camara.h"
#include "servo_ctrl.h"
#include "sensor.h"
#include "red.h"

#include <WiFi.h>
#include <esp_task_wdt.h>

/* ==========================================================================
 * Definiciones de la maquina de estados
 * ========================================================================== */
enum class Estado {
    INICIO,          /* esperando la conexion WiFi                     */
    REPOSO,          /* idle: espera de disparo (IR, boton o "t")      */
    CAPTURANDO,      /* flash + captura de frame                        */
    ENVIANDO,        /* envio HTTP multipart + parsing de la respuesta  */
    ACCIONANDO,      /* moviendo el servo al angulo recibido            */
    ESPERA_CAIDA,    /* espera no bloqueante de la caida del residuo    */
    REGRESANDO,      /* regreso del servo a 90 grados                   */
    ERROR_ESTADO      /* error con recuperacion                         */
};

/* Modos del LED rojo (GPIO 33, activo en LOW). */
enum class ModoLed {
    APAGADO,         /* reposo                                          */
    ENCENDIDO,       /* procesando                                      */
    PARPADEO_LENTO,  /* conectando WiFi                                 */
    TRES_ALERTAS     /* 3 parpadeos rapidos = error de envio            */
};

/* ==========================================================================
 * Variables de estado del ciclo
 * ========================================================================== */
static Estado estado = Estado::INICIO;
static unsigned long etapaDesdeMs = 0;
static unsigned long ultimoLogWifiMs = 0;
static int fallosConsecutivos = 0;
static int anguloClasificado = SERVO_ANGULO_REPOSO;
static camera_fb_t *fbEnCurso = nullptr;
static String errorUltimo = "";
static String lineaSerial = "";

/* ==========================================================================
 * Indicador LED rojo: maquina de parpadeos no bloqueante
 * ========================================================================== */
static struct {
    ModoLed modo = ModoLed::APAGADO;
    bool fisico = false;          /* reflejo logico del pin              */
    unsigned long proximoCambioMs = 0;
    int parpadeos = 0;            /* contador para TRES_ALERTAS          */
} led;

static void ledFisico(bool encendido) {
    digitalWrite(PIN_LED_ROJO, encendido ? LED_ROJO_ACTIVO : LED_ROJO_INACTIVO);
    led.fisico = encendido;
}

static void ledActualizar(unsigned long ahora) {
    switch (led.modo) {
        case ModoLed::APAGADO:
            if (led.fisico) ledFisico(false);
            break;

        case ModoLed::ENCENDIDO:
            if (!led.fisico) ledFisico(true);
            break;

        case ModoLed::PARPADEO_LENTO:
            if ((ahora - led.proximoCambioMs) >= 500) {
                ledFisico(!led.fisico);
                led.proximoCambioMs = ahora;
            }
            break;

        case ModoLed::TRES_ALERTAS:
            if (led.parpadeos > 0) {
                if (!led.fisico && (ahora - led.proximoCambioMs) >= 150) {
                    ledFisico(true);
                    led.proximoCambioMs = ahora;
                } else if (led.fisico && (ahora - led.proximoCambioMs) >= 150) {
                    ledFisico(false);
                    led.parpadeos--;
                    led.proximoCambioMs = ahora;
                }
            } else if (led.fisico) {
                ledFisico(false);
            }
            break;
    }
}

/* ==========================================================================
 * Manejo de fallos: conteo, indicador y reinicio controlado
 * ========================================================================== */
static void registrarFallo(const String &motivo) {
    fallosConsecutivos++;
    errorUltimo = motivo;

    if (fbEnCurso != nullptr) {       /* nunca dejar un buffer sin liberar  */
        camaraLiberarBuffer(fbEnCurso);
        fbEnCurso = nullptr;
    }

    Serial.println("[SISTEMA] ERROR: " + motivo +
                   " (fallo consecutivo " + String(fallosConsecutivos) + ")");

    led.modo = ModoLed::TRES_ALERTAS;
    led.parpadeos = 3;
    led.proximoCambioMs = millis();

    etapaDesdeMs = millis();
    estado = Estado::ERROR_ESTADO;
}

/* ==========================================================================
 * Inicio de ciclo: ignora disparos si ya hay uno en curso
 * ========================================================================== */
static void iniciarCiclo() {
    if (estado != Estado::REPOSO) {
        Serial.println("[SENSOR] Ciclo en curso, disparo ignorado");
        return;
    }
    sensorLimpiarDisparos();      /* consume eventos pendientes            */
    Serial.println("[SENSOR] Disparo validado. Ciclo de clasificacion iniciado"
                   " (fallos consecutivos previos: " + String(fallosConsecutivos) + ")");
    led.modo = ModoLed::ENCENDIDO;   /* procesando                        */
    etapaDesdeMs = millis();
    estado = Estado::CAPTURANDO;
}

/* ==========================================================================
 * Modo de prueba por Serial (para validar el hardware):
 *   "t"    dispara un ciclo completo (igual que sensor/boton)
 *   "s90"  mueve el servo a 90 grados
 *   "c"    captura una foto y reporta su tamano en bytes
 * ========================================================================== */
static void procesarComando(const String &cmd) {
    if (cmd == "t") {
        Serial.println("[CMD] Disparo manual (t) solicitado");
        iniciarCiclo();

    } else if (cmd.startsWith("s")) {
        int angulo = atoi(cmd.c_str() + 1);
        if (estado == Estado::REPOSO) {
            servoMover(angulo);
            Serial.println("[CMD] Servo movido a " + String(angulo) + " grados");
        } else {
            Serial.println("[CMD] Comando ignorado (ciclo en curso)");
        }

    } else if (cmd == "c") {
        if (estado == Estado::REPOSO) {
            camera_fb_t *fb = camaraCapturarJpeg();
            if (fb != nullptr) {
                Serial.println("[CMD] Foto OK, tamano " + String(fb->len) +
                               " bytes (" + String(fb->width) + "x" +
                               String(fb->height) + ")");
                camaraLiberarBuffer(fb);
            } else {
                Serial.println("[CMD] Error al capturar foto");
            }
        } else {
            Serial.println("[CMD] Comando ignorado (ciclo en curso)");
        }

    } else {
        Serial.println("[CMD] Comando desconocido: '" + cmd +
                       "' (usa: t, s<angulo> o c)");
    }
}

static void leerComandosSerial() {
    while (Serial.available()) {
        char c = (char)Serial.read();
        if (c == '\n') {
            lineaSerial.trim();
            if (lineaSerial.length() > 0) {
                procesarComando(lineaSerial);
            }
            lineaSerial = "";
        } else if (c != '\r' && lineaSerial.length() < 32) {
            lineaSerial += c;
        }
    }
}

/* ==========================================================================
 * setup
 * ========================================================================== */
void setup() {
    Serial.begin(SERIAL_BAUD);
    delay(300);
    Serial.println();
    Serial.println("============================================================");
    Serial.println(" " + String(NOMBRE_NODO) + " v" + String(VERSION_FIRMWARE));
    Serial.println(" ESTADO: NO VERIFICADO EN HARDWARE");
    Serial.println("============================================================");

    /* Watchdog de la tarea principal. */
    esp_task_wdt_init(WDT_TIMEOUT_SEGUNDOS, true);   /* panic si se desborda */
    esp_task_wdt_add(NULL);

    /* LEDs. */
    pinMode(PIN_LED_FLASH, OUTPUT);
    pinMode(PIN_LED_ROJO, OUTPUT);
    ledFisico(false);

    /* 1) Camara primero (reserva timer LEDC 0 / canal 0 para XCLK). */
    if (!camaraIniciar()) {
        Serial.println("[SISTEMA] Fallo critico de camara. Reinicio controlado...");
        esp_task_wdt_reset();
        delay(300);
        ESP.restart();
    }

    /* 2) Servo: reserva timers LEDC 2 y 3 y deja el servo en reposo (90). */
    servoIniciar();

    /* 3) Sensor IR y boton. */
    sensorIniciar();

    /* 4) WiFi asincrono con reconexion automatica. */
    redIniciar();

    led.modo = ModoLed::PARPADEO_LENTO;    /* conectando WiFi              */
    etapaDesdeMs = millis();
    estado = Estado::INICIO;

    Serial.println("[SISTEMA] Setup completado. Estados: INICIO (WiFi) -> REPOSO.");
    Serial.println("[SISTEMA] Prueba por Serial: 't' (ciclo), 's90' (servo), 'c' (foto).");
}

/* ==========================================================================
 * loop: maquina de estados no bloqueante
 * ========================================================================== */
void loop() {
    esp_task_wdt_reset();           /* alimenta el watchdog cada iteracion */
    unsigned long ahora = millis();

    ledActualizar(ahora);
    leerComandosSerial();

    switch (estado) {

        case Estado::INICIO:
            if (redConectada()) {
                Serial.println("[RED] WiFi conectada. IP: " + WiFi.localIP().toString());
                led.modo = ModoLed::APAGADO;
                estado = Estado::REPOSO;
                etapaDesdeMs = ahora;
            } else if ((ahora - ultimoLogWifiMs) >= 10000) {
                Serial.println("[RED] Conectando a WiFi... estado=" +
                               String(WiFi.status()));
                ultimoLogWifiMs = ahora;
            }
            break;

        case Estado::REPOSO:
            if (sensorDisparoIR()) {
                Serial.println("[SENSOR] Deteccion por sensor IR");
                iniciarCiclo();
            } else if (sensorBotonPresionado()) {
                Serial.println("[SENSOR] Disparo por boton manual");
                iniciarCiclo();
            }
            break;

        case Estado::CAPTURANDO:
            fbEnCurso = camaraCapturarJpeg();
            if (fbEnCurso != nullptr) {
                estado = Estado::ENVIANDO;
            } else {
                registrarFallo("Fallo al capturar imagen");
            }
            break;

        case Estado::ENVIANDO:
            if (fbEnCurso == nullptr) {
                registrarFallo("Buffer nulo llegando a ENVIANDO");
                break;
            }
            {
                RespuestaClasificacion res;
                if (redEnviarCaptura(fbEnCurso->buf, fbEnCurso->len, res)) {
                    camaraLiberarBuffer(fbEnCurso);
                    fbEnCurso = nullptr;

                    anguloClasificado = res.angulo;
                    fallosConsecutivos = 0;      /* bucle sano de nuevo     */
                    Serial.println("[SISTEMA] Clasificacion OK: categoria=" +
                                   res.categoria + " confianza=" +
                                   String(res.confianza, 3) +
                                   " -> servo a " + String(anguloClasificado));
                    etapaDesdeMs = millis();
                    estado = Estado::ACCIONANDO;
                } else {
                    camaraLiberarBuffer(fbEnCurso);
                    fbEnCurso = nullptr;
                    registrarFallo(res.error);
                }
            }
            break;

        case Estado::ACCIONANDO:
            servoMover(anguloClasificado);
            etapaDesdeMs = millis();
            estado = Estado::ESPERA_CAIDA;
            break;

        case Estado::ESPERA_CAIDA:
            if ((millis() - etapaDesdeMs) >= TIEMPO_ESPERA_CAIDA_MS) {
                Serial.println("[SERVO] Tiempo de caida agotado. "
                               "Regresando a reposo (90).");
                servoMover(SERVO_ANGULO_REPOSO);
                etapaDesdeMs = millis();
                estado = Estado::REGRESANDO;
            }
            break;

        case Estado::REGRESANDO:
            if ((millis() - etapaDesdeMs) >= SERVO_ACOMODAR_MS) {
                led.modo = ModoLed::APAGADO;
                estado = Estado::REPOSO;
            }
            break;

        case Estado::ERROR_ESTADO:
            if ((millis() - etapaDesdeMs) >= ERROR_DURACION_MS) {
                led.modo = ModoLed::APAGADO;

                if (fallosConsecutivos >= MAX_FALLOS_CONSECUTIVOS) {
                    Serial.println("[SISTEMA] Alcanzados " +
                                   String(MAX_FALLOS_CONSECUTIVOS) +
                                   " fallos consecutivos. Reinicio controlado...");
                    esp_task_wdt_reset();
                    delay(300);
                    ESP.restart();
                }

                if (!redConectada()) {
                    redReconectarSiCaida();
                }
                estado = Estado::REPOSO;
            }
            break;
    }
}