/*
 * ResiData - Nodo IoT
 * camara.cpp: implementacion de la camara OV2640 (placa AI-Thinker).
 *
 * ESTADO: NO VERIFICADO EN HARDWARE
 *  - La configuracion de pines sigue la tarjeta AI-Thinker estandar, pero
 *    requiere validacion en placa (docs/pruebas_hardware.md).
 */

#include "config.h"
#include "camara.h"

static const char *TAG = "[CAM]";

/* --------------------------------------------------------------------------
 * Configuracion estatica de la camara. La camara reserva el timer LEDC 0 y
 * el canal 0 para generar la senal XCLK; por eso el servo DEBE usar otros
 * timers (ver servo_ctrl.cpp y el paso 4 de pruebas_hardware.md).
 * -------------------------------------------------------------------------- */
static camera_config_t g_configCamara = {
    .pin_pwdn   = PIN_CAM_PWDN,
    .pin_reset  = PIN_CAM_RESET,
    .pin_xclk   = PIN_CAM_XCLK,
    .pin_sccb_sda = PIN_CAM_SIOD,
    .pin_sccb_scl = PIN_CAM_SIOC,

    .pin_d7 = PIN_CAM_Y9,   /* Y9  -> D7 */
    .pin_d6 = PIN_CAM_Y8,   /* Y8  -> D6 */
    .pin_d5 = PIN_CAM_Y7,   /* Y7  -> D5 */
    .pin_d4 = PIN_CAM_Y6,   /* Y6  -> D4 */
    .pin_d3 = PIN_CAM_Y5,   /* Y5  -> D3 */
    .pin_d2 = PIN_CAM_Y4,   /* Y4  -> D2 */
    .pin_d1 = PIN_CAM_Y3,   /* Y3  -> D1 */
    .pin_d0 = PIN_CAM_Y2,   /* Y2  -> D0 */

    .pin_vsync = PIN_CAM_VSYNC,
    .pin_href  = PIN_CAM_HREF,
    .pin_pclk  = PIN_CAM_PCLK,

    .xclk_freq_hz = 20000000,      /* 20 MHz, valor tipico ESP32-CAM     */
    .ledc_timer   = LEDC_TIMER_0,  /* reservado por la camara            */
    .ledc_channel = LEDC_CHANNEL_0,

    .pixel_format = PIXFORMAT_JPEG,
    .frame_size   = CAM_FRAME_SIZE,      /* SVGA 800x600                  */
    .jpeg_quality = CAM_JPEG_QUALITY,    /* calidad JPEG 12               */
    .fb_count     = CAM_FB_COUNT,        /* 2 buffers, requiere PSRAM     */
    .fb_location  = CAMERA_FB_IN_PSRAM,
    .grab_mode    = CAM_GRAB_MODE        /* CAMERA_GRAB_LATEST            */
};

bool camaraIniciar() {
    /* Enciende el flash GPIO4 como salida (uso dentro de captura). */
    pinMode(PIN_LED_FLASH, OUTPUT);
    flashApagar();

    esp_err_t err = esp_camera_init(&g_configCamara);
    if (err != ESP_OK) {
        Serial.printf(TAG " FALLO inicializando camara: 0x%x\n", err);
        return false;
    }

    /* Refuerza los parametros de captura por si el sensor trae otros. */
    sensor_t *s = esp_camera_sensor_get();
    if (s != nullptr) {
        s->set_framesize(s, CAM_FRAME_SIZE);
        s->set_quality(s, CAM_JPEG_QUALITY);
    }

    Serial.println(TAG " Camara inicializada (SVGA 800x600, JPEG q" +
                   String(CAM_JPEG_QUALITY) + ", fb_count=" +
                   String(CAM_FB_COUNT) + " PSRAM)");
    return true;
}

void flashEncender() {
    digitalWrite(PIN_LED_FLASH, HIGH);
}

void flashApagar() {
    digitalWrite(PIN_LED_FLASH, LOW);
}

camera_fb_t *camaraCapturarJpeg() {
    /* 1) Flash encendido y breve estabilizacion. */
    flashEncender();
    delay(CAM_FLASH_ESTABILIZAR_MS);

    /* 2) Captura. Con fb_count=2 + GRAB_LATEST no se bloquea esperando
          la exposicion completa del frame previo. */
    camera_fb_t *fb = esp_camera_fb_get();

    /* 3) Flash apagado SIEMPRE, incluso si la captura fallo. */
    flashApagar();

    if (fb == nullptr) {
        Serial.println(TAG " Error: esp_camera_fb_get devolvio NULL");
        return nullptr;
    }

    Serial.println(TAG " Frame capturado: " + String(fb->len) + " bytes");
    return fb;
}

void camaraLiberarBuffer(camera_fb_t *fb) {
    if (fb != nullptr) {
        esp_camera_fb_return(fb);
        fb = nullptr;
    }
}