/*
 * ResiData - Nodo IoT
 * camara.h: interfaz de la camara OV2640 de la placa AI-Thinker ESP32-CAM.
 *
 * ESTADO: NO VERIFICADO EN HARDWARE
 *  - La inicializacion y la captura deben comprobarse en placa (paso 2 de
 *    docs/pruebas_hardware.md) antes de confiar en el ciclo completo.
 */

#pragma once

#include <Arduino.h>
#include <esp_camera.h>

/*
 * Inicializa la camara OV2640 en 800x600 JPEG calidad 12 con doble buffer
 * en PSRAM y grabacion en modo LATEST. Devuelve true si esp_camera_init
 * retorna ESP_OK.
 */
bool camaraIniciar();

/*
 * Enciende el flash, estabiliza brevemente, captura un frame y apaga el
 * flash. Devuelve el frame buffer o nullptr en caso de error.
 * El buffer capturado DEBE liberarse siempre con camaraLiberarBuffer().
 */
camera_fb_t *camaraCapturarJpeg();

/* Libera SIEMPRE el frame buffer tras usarlo (esp_camera_fb_return). */
void camaraLiberarBuffer(camera_fb_t *fb);

/* Control del LED flash blanco (GPIO 4). */
void flashEncender();
void flashApagar();