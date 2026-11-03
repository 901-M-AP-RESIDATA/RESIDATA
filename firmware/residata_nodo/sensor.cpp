/*
 * ResiData - Nodo IoT
 * sensor.cpp: implementacion del sensor IR y del boton manual.
 *
 * Disparo por interrupcion (ISR minima):
 *   - La ISR (IRAM_ATTR) solo actualiza una bandera volatile y aplica un
 *     debounce por software de SENSOR_DEBOUNCE_MS (>= 150 ms).
 *   - Sin delays dentro de la ISR; millis() es seguro de llamar en
 *     contexto ISR en arduino-esp32.
 *
 * ESTADO: NO VERIFICADO EN HARDWARE
 */

#include "config.h"
#include "sensor.h"

static volatile bool g_irActivado = false;
static volatile uint32_t g_ultimaActivacionIrMs = 0;

void IRAM_ATTR onDisparoIr() {
    uint32_t ahora = millis();
    if ((ahora - g_ultimaActivacionIrMs) >= SENSOR_DEBOUNCE_MS) {
        g_ultimaActivacionIrMs = ahora;
        g_irActivado = true;
    }
}

void sensorIniciar() {
    g_irActivado = false;
    g_ultimaActivacionIrMs = 0;

    /* Sensor IR de salida digital (tipo E18-D80NK de colector abierto:
       necesita pull-up externo a 3.3 V; nunca 5 V a este pin). */
    pinMode(PIN_SENSOR_IR, INPUT);
    attachInterrupt(digitalPinToInterrupt(PIN_SENSOR_IR), onDisparoIr, FALLING);

    /* Boton manual a GND con pull-up interno. */
    pinMode(PIN_BOTON, INPUT_PULLUP);

    Serial.println("[SENSOR] Sensor IR (GPIO " + String(PIN_SENSOR_IR) +
                   ", FALLING, debounce " + String(SENSOR_DEBOUNCE_MS) +
                   " ms) y boton (GPIO " + String(PIN_BOTON) +
                   ", INPUT_PULLUP) inicializados");
}

bool sensorDisparoIR() {
    bool activo = g_irActivado;
    g_irActivado = false;
    return activo;
}

bool sensorBotonPresionado() {
    static bool estadoAnterior = HIGH;   /* pull-up: en reposo = HIGH */
    static uint32_t ultimoCambioMs = 0;

    bool actual = (digitalRead(PIN_BOTON) == LOW);

    /* Solo reporta el flanco de bajada (una pulsacion = un disparo). */
    if (actual != estadoAnterior &&
        (millis() - ultimoCambioMs) >= BOTON_DEBOUNCE_MS) {
        ultimoCambioMs = millis();
        estadoAnterior = actual;
        return actual;
    }
    return false;
}

void sensorLimpiarDisparos() {
    g_irActivado = false;
}