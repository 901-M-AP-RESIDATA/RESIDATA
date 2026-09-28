# ResiData - Sistema Inteligente de Gestión de Residuos

**ResiData** es una solución integral de clasificación e inteligencia de residuos en tiempo real. Mediante dispositivos físicos de bajo costo en el punto de depósito, el sistema captura imágenes, las procesa al instante usando Inteligencia Artificial, y acciona mecanismos automáticos para la separación correcta de la basura.

## Descripción del Proyecto

Sistema distribuido basado en arquitectura **Cliente Ligero / Servidor Centralizado en Red Local**. Consiste en nodos IoT que actúan como interfaces sensoriales y mecánicas, mientras que el procesamiento pesado (IA y Lógica de Negocio) reside en un servidor local de alto rendimiento.

El sistema también provee a los administradores un panel web con métricas operativas, almacenamiento de históricos y alertas automáticas, optimizando costos y garantizando un control estricto de materiales.

## Funcionalidades Principales

* **Captura visual en el borde:** Uso de cámara embebida (ESP32-CAM) accionada por proximidad.

* **Transmisión en tiempo real:** Comunicación vía Wi-Fi local al servidor.

* **Clasificación por IA:** Detección de colores y etiquetas de peligrosidad (Orgánico, Inorgánico, Peligroso) en menos de 2 segundos.

* **Accionamiento mecánico automatizado:** Control de servomotor SG90 según el dictamen de la IA.

* **Panel de control Web:** Dashboard en tiempo real (WebSockets) con reportes, históricos y alertas visuales.

## Stack Tecnológico

| Componente | Tecnologías | Descripción | 
 | ----- | ----- | ----- | 
| **Hardware / IoT** | `C++`, `ESP32-CAM`, `Servo SG90` | Captura de imagen y ejecución del mecanismo de separación. | 
| **Backend** | `Python`, `FastAPI` | API REST de alto rendimiento y orquestación. | 
| **Inteligencia Artificial** | `Modelos de Visión Artificial` | Inferencia visual ejecutada en el servidor local. | 
| **Base de Datos** | `PostgreSQL` | Almacenamiento relacional de históricos y catálogos. | 
| **Frontend Web** | `Svelte`, `WebSockets` | UI reactiva para el panel de administración. | 

## Arquitectura del Sistema

1. **Nodo IoT:** Detecta el residuo, captura la fotografía y hace un POST vía HTTP al servidor.

2. **Servidor Local:** Recibe la imagen, la procesa por el modelo de IA y calcula el ángulo de giro según las reglas de negocio.

3. **Respuesta y Acción:** El servidor responde al nodo con el ángulo (JSON); el ESP32 genera la señal PWM para girar el servo y depositar el residuo.

4. **Persistencia y Monitoreo:** El backend guarda el registro en PostgreSQL y emite un evento WebSocket para actualizar la vista del administrador de forma instantánea.

## Historias de Usuario (Product Backlog)

El desarrollo está guiado por las siguientes Historias de Usuario principales:

* **HU-01:** Captura de Imagen en el Borde.

* **HU-02:** Transmisión de Imagen al Servidor.

* **HU-03:** Recepción y Validación de Datos en Backend.

* **HU-04:** Procesamiento del Modelo de IA.

* **HU-05:** Lógica de Clasificación Mecánica.

* **HU-06:** Accionamiento Físico del Servomotor.

* **HU-07:** Persistencia de Históricos en Base de Datos.

* **HU-08:** Actualización del Dashboard en Tiempo Real.

* **HU-09:** Notificación de Residuos Peligrosos.

* **HU-10:** Reportes y Filtrado de Históricos.

## Equipo de Desarrollo

Este proyecto fue desarrollado para la evaluación de **Administración de Proyectos** en la **Universidad Tecnológica de Nezahualcóyotl** (División de Informática y Computación).

**Integrantes (Grupo ITIC-901):**

* Arciniega Ximello José Manuel
* Correa Gress Nicole
* Estrada Macías Víctor Hugo
* González Chávez Celestino Jair
* Manríquez Morales Juan Carlos
* Méndez González Roberto Carlos

**Asesora:** Profesora Margarita Larios