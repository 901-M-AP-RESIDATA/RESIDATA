/*
 * ResiData - Nodo IoT
 * red.cpp: WiFi + envio multipart manual al backend FastAPI.
 *
 * DISENO DEL MULTIPART MANUAL:
 *   HTTPClient no implementa multipart nativo, por eso la peticion se
 *   construye a mano y se envia con WiFiClient por bloques:
 *
 *   POST /api/v1/dispositivo/clasificar HTTP/1.1
 *   Host: <SERVER_HOST>:<SERVER_PORT>
 *   User-Agent: residata-nodo/1.0.0
 *   X-API-Key: <API_KEY>
 *   Content-Type: multipart/form-data; boundary=----ResiDataFormBoundary
 *   Content-Length: <len>
 *
 *   --boundary\r\n
 *   Content-Disposition: form-data; name="contenedor_id"\r\n
 *   \r\n
 *   <CONTENEDOR_ID>\r\n
 *   --boundary\r\n
 *   Content-Disposition: form-data; name="imagen"; filename="captura.jpg"\r\n
 *   Content-Type: image/jpeg\r\n
 *   \r\n
 *   <JPEG RAW>\r\n
 *   --boundary--\r\n
 *
 * Nota: el backend ResiData se autentica mediante la cabecera X-API-Key;
 * el campo "contenedor_id" es informativo y lo ignora. No confundir con el
 * campo "contenedor_id" de otros endpoints.
 *
 * ESTADO: NO VERIFICADO EN HARDWARE
 */

#include "config.h"
#include "red.h"

#include <WiFi.h>
#include <ArduinoJson.h>
#include <esp_task_wdt.h>

#if __has_include("secrets.h")
    #include "secrets.h"
#else
    #error "Falta secrets.h. Copia secrets.h.example a secrets.h y configura las credenciales."
#endif

static const char *TAG = "[RED]";
static const char *RUTA_CLASIFICAR = "/api/v1/dispositivo/clasificar";

/* --------------------------------------------------------------------------
 * Construye y envia una peticion POST multipart con WiFiClient.
 * Devuelve false si falla la conexion/envio; si hay respuesta, extrae el
 * codigo HTTP y el cuerpo JSON.
 * -------------------------------------------------------------------------- */
static bool enviarPeticion(const uint8_t *jpeg, size_t tamano,
                           int &codigoHttp, String &cuerpo) {
    const String boundary = "----ResiDataFormBoundary";

    /* Cuerpo multipart textual (sin el JPEG, que es binario). */
    String preImagen;
    preImagen += "--" + boundary + "\r\n";
    preImagen += "Content-Disposition: form-data; name=\"contenedor_id\"\r\n\r\n";
    preImagen += String(CONTENEDOR_ID) + "\r\n";
    preImagen += "--" + boundary + "\r\n";
    preImagen += "Content-Disposition: form-data; name=\"imagen\"; filename=\"captura.jpg\"\r\n";
    preImagen += "Content-Type: image/jpeg\r\n\r\n";

    String postImagen = "\r\n--" + boundary + "--\r\n";

    /* Cabeceras (sin el CRLF final, se contabiliza con Content-Length). */
    String cabeceras;
    cabeceras += String("POST ") + RUTA_CLASIFICAR + " HTTP/1.1\r\n";
    cabeceras += "Host: " + String(SERVER_HOST) + ":" + String(SERVER_PORT) + "\r\n";
    cabeceras += "User-Agent: " + String(NOMBRE_NODO) + "/" + String(VERSION_FIRMWARE) + "\r\n";
    cabeceras += "X-API-Key: " + String(API_KEY) + "\r\n";
    cabeceras += "Content-Type: multipart/form-data; boundary=" + boundary + "\r\n";

    size_t tamCuerpo = preImagen.length() + tamano + postImagen.length();
    cabeceras += "Content-Length: " + String(tamCuerpo) + "\r\n\r\n";

    /* Conexion con timeout propio (5 s). */
    WiFiClient cliente;
    if (!cliente.connect(SERVER_HOST, SERVER_PORT, RED_TIMEOUT_CONEXION_MS)) {
        Serial.println(TAG " Fallo de conexion TCP a " +
                       String(SERVER_HOST) + ":" + String(SERVER_PORT));
        return false;
    }

    Serial.println(TAG " Enviando " + String(tamCuerpo) + " bytes a " +
                   RUTA_CLASIFICAR);

    /* Envio por bloques desde el buffer, sin copiar el JPEG. */
    size_t enviados = cliente.print(cabeceras) +
                      cliente.print(preImagen) +
                      cliente.write(jpeg, tamano) +
                      cliente.print(postImagen);

    if (enviados < (cabeceras.length() + preImagen.length() + tamano + postImagen.length())) {
        Serial.println(TAG " Envio incompleto (bytes: " + String(enviados) + ")");
        cliente.stop();
        return false;
    }

    /* Lectura de la respuesta con deadline de RED_TIMEOUT_LECTURA_MS.
       Se refresca el plazo cada vez que llegan datos y se alimenta el
       watchdog durante la espera. */
    String respuesta;
    unsigned long inicio = millis();
    bool fin = false;

    while ((millis() - inicio) < RED_TIMEOUT_LECTURA_MS && !fin) {
        while (cliente.available()) {
            char c = (char)cliente.read();
            respuesta += c;
            inicio = millis();               /* hay datos: extiende el plazo */
            if (respuesta.length() > 8192) { /* limite de seguridad          */
                fin = true;
                break;
            }
        }
        esp_task_wdt_reset();
        if (!cliente.connected() && !cliente.available()) {
            break;                           /* servidor cerro la conexion    */
        }
        delay(10);
    }
    cliente.stop();

    if (respuesta.length() == 0) {
        Serial.println(TAG " Sin respuesta del servidor (timeout)");
        return false;
    }

    /* Codigo HTTP de la primera linea. */
    if (respuesta.startsWith("HTTP/1.1 ") || respuesta.startsWith("HTTP/1.0 ")) {
        codigoHttp = respuesta.substring(9, 12).toInt();
    } else {
        Serial.println(TAG " Respuesta sin linea HTTP valida");
        return false;
    }

    /* Cuerpo = todo lo que hay despues de la separacion de cabeceras. */
    int pos = respuesta.indexOf("\r\n\r\n");
    cuerpo = (pos >= 0) ? respuesta.substring(pos + 4) : "";
    return true;
}

/* -------------------------------------------------------------------------- */

bool redIniciar() {
    WiFi.mode(WIFI_STA);
    WiFi.setSleep(false);            /* evita latencia extra en la captura */
    WiFi.setAutoReconnect(true);
    WiFi.begin(WIFI_SSID, WIFI_PASS);

    Serial.println(TAG " WiFi STA iniciado (SSID ocultado en logs, "
                       "reconexion automatica activa)");
    return true;
}

bool redConectada() {
    return WiFi.status() == WL_CONNECTED;
}

void redReconectarSiCaida() {
    if (WiFi.status() == WL_CONNECTED) {
        return;
    }
    Serial.println(TAG " WiFi caida (estado " + String(WiFi.status()) +
                       "). Reconectando...");
    WiFi.disconnect(false);
    delay(WIFI_RECONEXION_ESPERA_MS);
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASS);
}

bool redEnviarCaptura(const uint8_t *jpeg, size_t tamano,
                      RespuestaClasificacion &respuesta) {
    respuesta.ok = false;
    respuesta.error = "";

    Serial.println(TAG " Inicio envio de " + String(tamano) + " bytes");

    bool exito = false;
    int codigoHttp = 0;
    String cuerpo;
    int intento = 0;               /* 1 envio inicial + hasta 3 reintentos */

    while (intento <= RED_MAX_REINTENTOS && !exito) {
        if (WiFi.status() != WL_CONNECTED) {
            Serial.println(TAG " WiFi no conectada antes del intento. Reconectando...");
            redReconectarSiCaida();
            esp_task_wdt_reset();
        }

        /* Backoff exponencial entre reintentos: 500 ms, 1 s, 2 s. */
        if (intento > 0) {
            uint16_t espera = (intento - 1 < RED_BACKOFF_COUNT)
                                  ? RED_BACKOFF_MS[intento - 1]
                                  : RED_BACKOFF_MS[RED_BACKOFF_COUNT - 1];
            Serial.println(TAG " Reintento " + String(intento) + "/" +
                           String(RED_MAX_REINTENTOS) + " en " +
                           String(espera) + " ms");
            unsigned long marca = millis();
            while ((millis() - marca) < espera) {
                esp_task_wdt_reset();
                delay(10);
            }
        }

        codigoHttp = 0;
        cuerpo = "";

        if (enviarPeticion(jpeg, tamano, codigoHttp, cuerpo)) {
            if (codigoHttp == 200) {
                exito = true;
            } else {
                Serial.println(TAG " El servidor respondio HTTP " +
                               String(codigoHttp));
            }
        } else {
            Serial.println(TAG " Fallo de red en el intento " +
                           String(intento + 1));
        }
        intento++;
    }

    if (!exito) {
        respuesta.error = "Envio fallido (ultimo codigo HTTP " +
                          String(codigoHttp) + ")";
        if (codigoHttp == 401) {
            respuesta.error += " - API key invalida";
        } else if (codigoHttp == 404) {
            respuesta.error += " - contenedor inexistente";
        } else if (codigoHttp == 400) {
            respuesta.error += " - imagen invalida";
        }
        Serial.println(TAG " " + respuesta.error);
        return false;
    }

    /* Parsing de la respuesta JSON con ArduinoJson (v7). */
    JsonDocument doc;
    DeserializationError err = deserializeJson(doc, cuerpo);
    if (err) {
        respuesta.error = "JSON invalido en la respuesta: " + String(err.c_str());
        Serial.println(TAG " " + respuesta.error);
        return false;
    }

    if (!doc["angulo"].is<int>()) {
        respuesta.error = "Respuesta sin campo 'angulo' valido";
        Serial.println(TAG " " + respuesta.error + ". Cuerpo: " + cuerpo);
        return false;
    }

    int angulo = doc["angulo"].as<int>();
    if (angulo < 0 || angulo > 180) {
        respuesta.error = "'angulo' fuera de rango [0,180]: " + String(angulo);
        Serial.println(TAG " " + respuesta.error);
        return false;
    }

    respuesta.ok = true;
    respuesta.angulo = angulo;
    respuesta.categoria = doc["categoria"] | String("desconocida");
    respuesta.confianza = doc["confianza"] | 0.0f;

    Serial.println(TAG " Respuesta OK: angulo=" + String(angulo) +
                   " categoria=" + respuesta.categoria +
                   " confianza=" + String(respuesta.confianza, 3));
    return true;
}