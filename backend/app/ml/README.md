# Modelos de IA - ResiData

Esta carpeta contiene los pesos del modelo de visión artificial (YOLO)
que clasifica los residuos en **Orgánico**, **Inorgánico** y **Peligroso**.

## Estructura

```
app/ml/
├── README.md                 (este archivo)
├── pesos/                    (archivos de pesos, NO se versionan)
│   └── residuos_yolo.pt      (pesos entrenados, RUTA_MODELO por defecto)
└── __init__.py
```

## Modo simulado

Si el archivo indicado en la variable de entorno `RUTA_MODELO` **no existe**,
el backend arranca automáticamente en **MODO SIMULADO**: genera una
clasificación aleatoria ponderada (Orgánico 45 %, Inorgánico 35 %,
Peligroso 20 %) y registra una advertencia en el log. Esto permite
desarrollar y probar todo el flujo sin GPU ni dataset.

## Inferencia real

1. Instala las dependencias opcionales de IA:

   ```powershell
   pip install -r requirements-ml.txt
   ```

2. Coloca el archivo de pesos entrenado en `app/ml/pesos/residuos_yolo.pt`
   (o ajusta `RUTA_MODELO` en el `.env`).

3. Reinicia el backend. Verás en el log `Modelo YOLO cargado correctamente`.

## Entrenamiento

Consulta la guía paso a paso en
[`docs/entrenamiento_yolo.md`](../../docs/entrenamiento_yolo.md) para
entrenar el modelo gratis en Google Colab con un dataset de residuos.

## Mapeo de clases

El servicio `app/services/ia_yolo.py` traduce las etiquetas del modelo a las
tres categorías del sistema. Ajusta el diccionario `MAPA_CLASES` si tu
dataset usa otros nombres (por ejemplo `organico`, `vidrio`, `bateria`).
