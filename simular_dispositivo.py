#!/usr/bin/env python3
"""
Simulador de Nodo IoT ResiData para demostraciones sin hardware físico.
Emula el comportamiento exacto del microcontrolador ESP32-CAM enviando
fotografías reales al backend FastAPI y mostrando la respuesta mecánica.
"""

import sys
import time
import requests
from pathlib import Path
from PIL import Image, ImageDraw

def generar_imagen_prueba(nombre_archivo: str, color: str, texto: str):
    """Genera una imagen JPEG sintética que simula un residuo."""
    img = Image.new("RGB", (640, 480), color=color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 40, 600, 440], outline="white", width=4)
    draw.text((60, 220), texto, fill="white")
    img.save(nombre_archivo, "JPEG")

def simular_envio(url_api: str, api_key: str, contenedor_id: str, ruta_imagen: str):
    print("\n" + "="*60)
    print("🤖 [SIMULADOR ESP32-CAM] Detectando residuo por sensor IR...")
    time.sleep(0.8)
    print("📸 [SIMULADOR ESP32-CAM] Capturando frame SVGA con OV2640...")
    time.sleep(0.5)
    print(f"📡 [SIMULADOR ESP32-CAM] Transmitiendo imagen a {url_api}...")

    headers = {
        "X-Api-Key": api_key,
        "X-Contenedor-Id": contenedor_id
    }

    with open(ruta_imagen, "rb") as f:
        archivos = {"imagen": (Path(ruta_imagen).name, f, "image/jpeg")}
        inicio = time.time()
        try:
            resp = requests.post(
                f"{url_api}/api/v1/dispositivo/clasificar",
                headers=headers,
                files=archivos,
                timeout=10
            )
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return

    duracion = int((time.time() - inicio) * 1000)

    if resp.status_code == 200:
        datos = resp.json()
        categoria = datos.get('categoria_nombre') or datos.get('categoria')
        confianza = datos.get('confianza', 0.0)
        angulo = datos.get('angulo', 90)
        alerta = datos.get('alerta_generada') or datos.get('alerta_emitida') or False

        print(f"✅ [RESPUESTA DEL SERVIDOR] Recibida en {duracion} ms:")
        print(f"   • Categoría dictaminada : {categoria}")
        print(f"   • Confianza de la IA    : {confianza * 100:.1f} %")
        print(f"   • Ángulo para el Servo  : {angulo}°")
        print(f"   • Alerta de Peligro     : {'⚠️ SÍ' if alerta else 'No'}")
        print("\n⚙️ [ACCIÓN MECÁNICA]")
        if angulo == 0:
            print("   -> Servomotor gira a 0°: COMPUERTA VERDE ABIERTA (Orgánico)")
        elif angulo == 90:
            print("   -> Servomotor gira a 90°: COMPUERTA AZUL ABIERTA (Inorgánico)")
        else:
            print("   -> Servomotor gira a 180°: COMPUERTA ROJA ABIERTA (Residuo Peligroso)")
        print("   -> Esperando caída (3s) y regresando a posición de reposo.")
    else:
        print(f"❌ Error del servidor ({resp.status_code}): {resp.text}")

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    # 1. Crear 3 imágenes de prueba
    dir_pruebas = Path("imagenes_demo")
    dir_pruebas.mkdir(exist_ok=True)
    
    img_organico = dir_pruebas / "manzana.jpg"
    img_inorganico = dir_pruebas / "botella_plastico.jpg"
    img_peligroso = dir_pruebas / "bateria_quimica.jpg"
    
    generar_imagen_prueba(str(img_organico), "#2e7d32", "RESIDUO ORGANICO - MANZANA")
    generar_imagen_prueba(str(img_inorganico), "#1565c0", "RESIDUO INORGANICO - PLASTICO")
    generar_imagen_prueba(str(img_peligroso), "#c62828", "RESIDUO PELIGROSO - PILA/BATERIA")

    print("\n🚀 Selecciona qué residuo arrojar al contenedor simulado:")
    print("1. Manzana (Orgánico)")
    print("2. Botella de plástico (Inorgánico)")
    print("3. Pila / Batería (Peligroso)")
    print("4. Foto personalizada desde tu disco")
    
    opc = input("\nElige una opción (1-4) [default: 1]: ").strip() or "1"
    
    if opc == "1":
        seleccion = str(img_organico)
    elif opc == "2":
        seleccion = str(img_inorganico)
    elif opc == "3":
        seleccion = str(img_peligroso)
    else:
        seleccion = input("Ingresa la ruta de una foto JPG de tu computadora: ").strip()

    # API key del Contenedor Patio A (cargado en la base de datos)
    API_KEY = "cambia_esta_clave"
    simular_envio(url, API_KEY, "1", seleccion)
