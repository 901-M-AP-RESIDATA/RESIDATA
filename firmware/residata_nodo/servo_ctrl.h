/*
 * ResiData - Nodo IoT
 * servo_ctrl.h: control del servomotor SG90 (rampa/ruleta de clasificacion).
 *
 * ESTADO: NO VERIFICADO EN HARDWARE
 *  - El punto critico (conflicto de timers LEDC con la camara) debe
 *    verificarse en el paso 4 de docs/pruebas_hardware.md.
 */

#pragma once

#include <Arduino.h>
#include <ESP32Servo.h>

/*
 * Inicializa el servo:
 *   1. Reserva los timers LEDC 2 y 3 ANTES del attach (la camara ocupa el
 *      timer 0 / canal 0 para XCLK y no deben compartirse).
 *   2. escribe period 50 Hz, attach en el pin con pulsos 500..2400 us.
 *   3. Deja el servo en reposo (90 grados).
 */
void servoIniciar();

/* Mueve el servo al angulo indicado, limitado a [0, 180]. */
void servoMover(int angulo);

/* Devuelve el ultimo angulo comandado. */
int servoAnguloActual();