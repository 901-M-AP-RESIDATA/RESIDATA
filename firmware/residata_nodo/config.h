/*
 * ResiData - Nodo IoT (ESP32-CAM AI-Thinker)
 * config.h: pines, resoluciones, tiempos y reintentos del nodo.
 *
 * ESTADO: NO VERIFICADO EN HARDWARE
 *  - Escrito sin acceso a la placa fisica. Pending de validar en el
 *    hardware real siguiendo docs/pruebas_hardware.md.
 */

#pragma once

#include <Arduino.h>

/* ==========================================================================
 * Identificacion y version del firmware
 * ========================================================================== */
#define NOMBRE_NODO           "residata-nodo"
#define VERSION_FIRMWARE      "1.0.0"

/* ==========================================================================
 * Pines de usuario (tabla real del proyecto ResiData)
 * ========================================================================== */
#define PIN_LED_FLASH         4      /* LED flash blanco integrado        */
#define PIN_LED_ROJO          33     /* LED rojo integrado (activo en LOW) */
#define PIN_SERVO             14     /* Senal del servo SG90               */
#define PIN_SENSOR_IR         13     /* Sensor de proximidad IR (FALLING)  */
#define PIN_BOTON             15     /* Boton manual con INPUT_PULLUP      */

#define LED_ROJO_ACTIVO       LOW
#define LED_ROJO_INACTIVO     HIGH

/* ==========================================================================
 * Pines internos fijos de la camara OV2640 en la placa AI-Thinker.
 * NO deben modificarse: son el cableado interno de la placa.
 * ========================================================================== */
#define PIN_CAM_PWDN          32
#define PIN_CAM_RESET         -1
#define PIN_CAM_XCLK          0
#define PIN_CAM_SIOD          26
#define PIN_CAM_SIOC          27
#define PIN_CAM_Y9            35
#define PIN_CAM_Y8            34
#define PIN_CAM_Y7            39
#define PIN_CAM_Y6            36
#define PIN_CAM_Y5            21
#define PIN_CAM_Y4            19
#define PIN_CAM_Y3            18
#define PIN_CAM_Y2            5
#define PIN_CAM_VSYNC         25
#define PIN_CAM_HREF          23
#define PIN_CAM_PCLK          22

/* ==========================================================================
 * Configuracion de la camara
 * Objetivo de diseno: < 1 s desde la activacion hasta tener la imagen.
 * ========================================================================== */
#define CAM_FRAME_SIZE        FRAMESIZE_SVGA   /* 800x600               */
#define CAM_JPEG_QUALITY      12
#define CAM_FB_COUNT          2                /* requiere PSRAM         */
#define CAM_GRAB_MODE         CAMERA_GRAB_LATEST
#define CAM_FLASH_ESTABILIZAR_MS  80           /* flash encendido breve  */

/* ==========================================================================
 * Servomotor SG90 (rampa/ruleta de clasificacion)
 * ========================================================================== */
#define SERVO_FRECUENCIA_HZ   50
#define SERVO_US_MINIMO       500
#define SERVO_US_MAXIMO       2400
#define SERVO_ANGULO_REPOSO   90
#define SERVO_ACOMODAR_MS     700   /* espera para que el servo regrese  */

/* Timers LEDC reservados para el servo (la camara usa timer 0 / canal 0) */
#define SERVO_TIMER_LEDC_A    2
#define SERVO_TIMER_LEDC_B    3

#define TIEMPO_ESPERA_CAIDA_MS 3000  /* espera de caida del residuo      */

/* ==========================================================================
 * Sensor de proximidad IR y boton manual
 * ========================================================================== */
#define SENSOR_DEBOUNCE_MS    150   /* debounce minimo del disparo IR    */
#define BOTON_DEBOUNCE_MS     100

/* ==========================================================================
 * WiFi / red local (HTTP sin TLS)
 * ========================================================================== */
#define WIFI_TIMEOUT_CONEXION_MS  15000
#define WIFI_RECONEXION_ESPERA_MS 1000

#define RED_MAX_REINTENTOS    3     /* maximo de reintentos del envio    */
#define RED_TIMEOUT_CONEXION_MS   5000
#define RED_TIMEOUT_LECTURA_MS    8000

/* Backoff exponencial entre reintentos: 500 ms, 1 s, 2 s */
static const uint16_t RED_BACKOFF_MS[] = {500, 1000, 2000};
#define RED_BACKOFF_COUNT     3

/* ==========================================================================
 * Robustez: watchdog y reinicio controlado
 * ========================================================================== */
#define MAX_FALLOS_CONSECUTIVOS   3   /* reinicio tras N fallos seguidos */
#define WDT_TIMEOUT_SEGUNDOS      20
#define ERROR_DURACION_MS         6000  /* tiempo mostrando la alerta LED */

/* ==========================================================================
 * Serial
 * ========================================================================== */
#define SERIAL_BAUD           115200