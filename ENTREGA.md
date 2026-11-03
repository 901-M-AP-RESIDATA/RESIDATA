# ResiData — Entregas e Integración General (HU-01 a HU-10)

Documento consolidado de entregas del proyecto **ResiData** en la rama `develop`. Este repositorio reúne la integración completa de los componentes de hardware (firmware ESP32-CAM), backend (FastAPI), frontend (SvelteKit), modelos de IA (YOLO) y persistencia relacional (PostgreSQL).

Para consultar la matriz completa de dependencias, marcas de archivos compartidos y base de arquitectura, ver [MAPA_ENTREGAS.md](MAPA_ENTREGAS.md).

---

## 1. Resumen de Historias de Usuario

| ID | Historia de Usuario | Responsable | Rama / Origen | Reporte Individual |
| :--- | :--- | :--- | :--- | :--- |
| **HU-01** | Captura de Imagen en el Borde | Jose M. | `josem` | [HU-01_Captura-Imagen-Borde.md](entregas/HU-01_Captura-Imagen-Borde.md) |
| **HU-02** | Transmisión de Imagen al Servidor (API) | Victor | `origin/victor` | [HU-02_Transmision-Imagen-API.md](entregas/HU-02_Transmision-Imagen-API.md) |
| **HU-03** | Recepción y Validación de Datos en Backend | Jair | `origin/jair` | [HU-03_Recepcion-Validacion-Backend.md](entregas/HU-03_Recepcion-Validacion-Backend.md) |
| **HU-04** | Procesamiento del Modelo de IA | Nicole | `origin/nicole` | [HU-04_Modelo-IA.md](entregas/HU-04_Modelo-IA.md) |
| **HU-05** | Reglas de Clasificación Mecánica | Juan Carlos | `origin/JUANCARLOSMANMOR` / `ENTREGAS` | [HU-05_Reglas-Clasificacion.md](entregas/HU-05_Reglas-Clasificacion.md) |
| **HU-06** | Accionamiento Físico del Servomotor (SG90) | Roberto | `origin/roberto` | [HU-06_Servomotor-SG90.md](entregas/HU-06_Servomotor-SG90.md) |
| **HU-07** | Persistencia de Históricos en Base de Datos | Jair | `origin/jair` | [HU-07_Persistencia-Historicos.md](entregas/HU-07_Persistencia-Historicos.md) |
| **HU-08** | Actualización del Dashboard en Tiempo Real | Jose M. | `ENTREGAS` | [HU-08_Dashboard-Tiempo-Real.md](entregas/HU-08_Dashboard-Tiempo-Real.md) |
| **HU-09** | Notificación de Residuos Peligrosos | Juan Carlos | `origin/JUANCARLOSMANMOR` / `ENTREGAS` | [HU-09_Notificacion-Peligrosos.md](entregas/HU-09_Notificacion-Peligrosos.md) |
| **HU-10** | Reportes y Filtrado de Históricos | Nicole | `origin/nicole` | [HU-10_Reportes-Filtrado.md](entregas/HU-10_Reportes-Filtrado.md) |

---

## 2. Estructura de la Aplicación Integrada

```
RESIDATA/
├── README.md                                 # Descripción general y equipo
├── MAPA_ENTREGAS.md                          # Mapa maestro de asignación y alcance
├── ENTREGA.md                                # Este documento (índice consolidado)
├── entregas/                                 # Reportes técnicos individuales (HU-01 a HU-10)
├── backend/                                  # FastAPI + SQLAlchemy 2 + Alembic + pytest
│   ├── .env.example  .gitignore  alembic.ini
│   ├── alembic/
│   │   ├── env.py  script.py.mako
│   │   └── versions/0001_esquema_inicial.py  0002_datos_iniciales.py
│   ├── app/
│   │   ├── __init__.py  main.py
│   │   ├── api/__init__.py
│   │   │   └── v1/ __init__.py  alertas.py  auth.py  catalogos.py
│   │   │        contenedores.py  dashboard.py  dispositivo.py
│   │   │        historico.py  router.py  salud.py  usuarios.py  ws.py
│   │   ├── core/ __init__.py  config.py  deps.py  excepciones.py
│   │   │        logging.py  seguridad.py
│   │   ├── db/ __init__.py  base.py  modelos.py  sesion.py
│   │   ├── ml/ __init__.py  README.md  pesos/.gitkeep
│   │   ├── schemas/ __init__.py  alerta.py  auth.py  categoria.py  comun.py
│   │   │        contenedor.py  dashboard.py  dispositivo.py  historico.py
│   │   │        rol.py  usuario.py
│   │   └── services/ __init__.py  almacenamiento.py  contenedores.py
│   │            dashboard.py  ia_yolo.py  procesamiento.py  tiempo_real.py
│   │            usuarios.py
│   ├── requirements.txt  requirements-dev.txt  requirements-ml.txt
│   ├── scripts/crear_admin.py
│   ├── storage/imagenes/.gitkeep
│   └── tests/ __init__.py  test_api_integracion.py
├── database/
│   ├── 01_esquema.sql  02_datos_iniciales.sql
│   ├── 03_consultas_dashboard.sql  04_rollback.sql
│   └── README.md
├── docs/
│   ├── cableado.md  diagrama_er.md  diccionario_datos.md
│   └── instalacion_firmware.md  pruebas_hardware.md
├── firmware/residata_nodo/
│   ├── .gitignore  residata_nodo.ino  config.h
│   ├── camara.cpp/.h  sensor.cpp/.h  red.cpp/.h  servo_ctrl.cpp/.h
│   └── secrets.h.example
└── frontend/                                 # SvelteKit 5 + Tailwind 4 + Chart.js
    ├── .env.example  .gitignore  .npmrc  .vscode/extensions.json
    ├── package.json  package-lock.json  README.md  tsconfig.json  vite.config.ts
    ├── static/ favicon.svg  robots.txt
    └── src/
        ├── app.css  app.d.ts  app.html
        ├── lib/
        │   ├── config.ts  index.ts
        │   ├── api/ (cliente, index, auth, usuarios, contenedores, catalogos,
        │   │        almacenamiento, dashboard, alertas, historico, mock)
        │   ├── assets/favicon.svg
        │   ├── components/ (Boton, CampoSelect, CampoTexto, Cargando,
        │   │        EstadoVacio, Grafica, Insignia, Modal, Navbar, Sidebar,
        │   │        TablaReciente, Tarjeta, TarjetaMetrica, Toast)
        │   ├── stores/ (alertas, conexion, sesion, tiempoReal, toast)
        │   ├── tipos/index.ts
        │   └── util/ (csv.ts, formato.ts, sonido.ts)
        └── routes/
            ├── +error.svelte  +layout.svelte  +layout.ts  +page.svelte  +page.ts
            ├── login/ (+page.svelte, +page.ts)
            └── (panel)/ +layout.svelte  alertas/  contenedores/
                     dashboard/  historico/  usuarios/
```
