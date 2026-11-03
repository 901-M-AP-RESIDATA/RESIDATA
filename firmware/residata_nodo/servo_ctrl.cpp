/*
 * ResiData - Nodo IoT
 * servo_ctrl.cpp: implementacion del servomotor SG90.
 *
 * Resolucion del conflicto de timers LEDC:
 *   - La camara (esp_camera) usa el timer LEDC 0 y el canal 0 para XCLK.
 *   - ESP32Servo crea internamente un timer LEDC por canal PWM. Si se
 *     inicializa sin reservar, puede chocar con la camara y el XCLK
 *     deja de generar, rompiendo la captura.
 *   - Solucion (sigue la recomendacion del proyecto): reservar los timers
 *     2 y 3 con ESP32PWM::allocateTimer() ANTES de llamar a attach(), e
 *     inicializar la camara primero (orden impuesto desde setup()).
 *
 * ESTADO: NO VERIFICADO EN HARDWARE
 *  - El funcionamiento simultaneo camara + servo debe comprobarse en el
 *    paso 4 de docs/pruebas_hardware.md.
 */

#include "config.h"
#include "servo_ctrl.h"

static Servo sg90;
static int anguloActual = SERVO_ANGULO_REPOSO;
static bool servoListo = false;

void servoIniciar() {
    /* 1) Reservar timers LEDC para el servo antes del attach. */
    ESP32PWM::allocateTimer(SERVO_TIMER_LEDC_A);
    ESP32PWM::allocateTimer(SERVO_TIMER_LEDC_B);

    /* 2) 50 Hz (periodo de 20 ms) y pulsos de 500..2400 us. */
    sg90.setPeriodHertz(SERVO_FRECUENCIA_HZ);
    sg90.attach(PIN_SERVO, SERVO_US_MINIMO, SERVO_US_MAXIMO);

    servoListo = true;

    /* 3) Reposo a 90 grados. */
    anguloActual = SERVO_ANGULO_REPOSO;
    sg90.write(anguloActual);

    Serial.println("[SERVO] Iniciado: pin " + String(PIN_SERVO) +
                   ", 50 Hz, pulsos " + String(SERVO_US_MINIMO) + ".." +
                   String(SERVO_US_MAXIMO) + " us, reposo en " +
                   String(SERVO_ANGULO_REPOSO) + " grados (timers LEDC " +
                   String(SERVO_TIMER_LEDC_A) + " y " +
                   String(SERVO_TIMER_LEDC_B) + " reservados)");
}

void servoMover(int angulo) {
    if (!servoListo) {
        return;
    }
    angulo = constrain(angulo, 0, 180);
    if (angulo == anguloActual) {
        return;
    }
    sg90.write(angulo);
    anguloActual = angulo;
    Serial.println("[SERVO] Moviendo a " + String(angulo) + " grados");
}

int servoAnguloActual() {
    return anguloActual;
}