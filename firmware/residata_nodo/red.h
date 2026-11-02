/*
 * ResiData - Nodo IoT
 * red.h: conexion WiFi y envio multipart al backend FastAPI.
 *
 * ESTADO: NO VERIFICADO EN HARDWARE
 *  - El contrato HTTP (multipart manual + reintentos) debe validarse con
 *    el backend (paso 6 de docs/pruebas_hardware.md).
 */

#pragma once

#include <Arduino.h>

/* Resultado de una clasificacion recibida del servidor. */
struct RespuestaClasificacion {
    bool ok;              /* true si hubo respuesta 200 con angulo valido */
    int angulo;           /* angulo del servo [0, 180]                    */
    String categoria;     /* etiqueta devuelta por el backend             */
    float confianza;      /* confianza de la clasificacion (0..1)         */
    String error;         /* motivo en caso de error                       */
};

/*
 * Inicia el WiFi en modo STA con reconexion automatica. NO bloquea: la
 * conexion se completa en segundo plano y se verifica con redConectada().
 */
bool redIniciar();

/* true si hay conexion activa (WL_CONNECTED). */
bool redConectada();

/* Si el WiFi se cayo, lo reconecta (reconoce y vuelve a begin). */
void redReconectarSiCaida();

/*
 * Envia la imagen JPEG en multipart (campo "imagen", filename captura.jpg)
 * junto al campo "contenedor_id", con cabecera X-API-Key.
 * Aplica hasta RED_MAX_REINTENTOS reintentos con backoff exponencial
 * (RED_BACKOFF_MS) y valida que el codigo HTTP sea 200 y que el JSON traiga
 * "angulo" dentro de [0, 180]. Devuelve true solo en ese caso y rellena
 * 'respuesta'. En caso de error rellena 'respuesta.error' y devuelve false.
 *
 * Bloqueante: puede tardar varios segundos por los reintentos; el watchdog
 * se refresca internamente durante la espera.
 */
bool redEnviarCaptura(const uint8_t *jpeg, size_t tamano,
                      RespuestaClasificacion &respuesta);