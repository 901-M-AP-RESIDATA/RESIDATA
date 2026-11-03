/*
 * ResiData - Nodo IoT
 * sensor.h: sensor de proximidad IR (GPIO 13) y boton manual (GPIO 15).
 *
 * ESTADO: NO VERIFICADO EN HARDWARE
 *  - El disparo por interrupcion y el debounce deben validarse en el
 *    paso 5 de docs/pruebas_hardware.md.
 */

#pragma once

#include <Arduino.h>

/*
 * Inicializa el sensor IR con interrupcion FALLING y el boton como
 * entrada con pull-up interno.
 */
void sensorIniciar();

/*
 * Devuelve true si el sensor IR activo un disparo (y lo consume).
 * La bandera es ISR minima; el debounce de flanco se aplica en la ISR.
 */
bool sensorDisparoIR();

/*
 * Devuelve true en el flanco de bajada del boton (debounced). Usado junto
 * a sensorDisparoIR() como fuente alternativa de disparo.
 */
bool sensorBotonPresionado();

/* Limpia cualquier disparo pendiente (usar al iniciar un ciclo). */
void sensorLimpiarDisparos();

/* ISR del sensor IR. Se mantiene publica para poder adjuntarla. */
void IRAM_ATTR onDisparoIr();