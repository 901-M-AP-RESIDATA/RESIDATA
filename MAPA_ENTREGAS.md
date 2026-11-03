# MAPA DE ENTREGAS — ResiData (HU-01 a HU-10)

> **Documento de análisis. No se copió ningún archivo ni se creó ninguna carpeta de HU.**
> Generado el 2026-11-02.

## 0. Rutas y alcance

| Concepto | Ruta |
| --- | --- |
| App completa (solo lectura) | `C:\Users\victo\OneDrive\Imágenes\versiones de residata\RESIDATA completo` |
| Carpeta de entregas | `C:\Users\victo\OneDrive\Imágenes\ENTREGAS` (asumida) |
| Este mapa | `C:\Users\victo\OneDrive\Imágenes\ENTREGAS\MAPA_ENTREGAS.md` |

- **Sin Git/GitHub.** Cada HU será una carpeta independiente con la misma estructura interna que la app.
- **No se versionan** artefactos: `venv/`, `.venv/`, `node_modules/`, `build/`, `.svelte-kit/`, `__pycache__/`, `.pytest_cache/`.
- **Credenciales revisadas:** `backend/.env` solo difiere del ejemplo en `DATABASE_URL` (cadena local por defecto); `frontend/.env` es idéntico al ejemplo; `firmware/residata_nodo/secrets.h` conserva los placeholders del `.example`. **No hay credenciales reales**, pero los tres archivos quedan fuera de las entregas (§5).
- **Total de archivos a entregar: 148** (sin contar los excluidos de §5).

Leyenda:
- **[C]** archivo compartido por varias HU (se copia completo en la primera que lo necesita).
- **[B]** archivo de Base del proyecto (ver §4).
- **[?]** archivo sin HU propia en el backlog (ver §4.4).

---

## 1. Estructura de la app

```
RESIDATA completo/
├── README.md
├── backend/                          FastAPI + SQLAlchemy 2 + Alembic + pytest
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
└── frontend/                         SvelteKit 5 + Tailwind 4 + Chart.js
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

---

## 2. Resumen por entrega

| Carpeta | Archivos | Depende de |
| --- | --- | --- |
| `HU-01_Captura-Imagen-Borde` | 10 | — |
| `HU-02_Transmision-Imagen-API` | 4 | HU-01 |
| `HU-03_Recepcion-Validacion-Backend` | 38 | — (backend base) |
| `HU-04_Modelo-IA` | 5 | HU-03 |
| `HU-05_Reglas-Clasificacion` | 1 | HU-03, HU-04, HU-07 |
| `HU-06_Servomotor-SG90` | 2 | HU-01 |
| `HU-07_Persistencia-Historicos` | 15 | HU-03 |
| `HU-08_Dashboard-Tiempo-Real` | 59 | HU-03, HU-05, HU-07 |
| `HU-09_Notificacion-Peligrosos` | 9 | HU-05, HU-07, HU-08 |
| `HU-10_Reportes-Filtrado` | 5 | HU-03, HU-07, HU-08 |
| **Total** | **148** | |

---

## 3. Asignación detallada

### HU-01_Captura-Imagen-Borde
Responsable: Jose M. · Prioridad: Alta

| Archivo | Tarea técnica | Marca |
| --- | --- | --- |
| `firmware/residata_nodo/sensor.cpp` | Sensor IR por interrupción hardware (`FALLING`), debounce 150 ms, botón manual 100 ms | — |
| `firmware/residata_nodo/sensor.h` | Interfaz del sensor y de la ISR | — |
| `firmware/residata_nodo/camara.cpp` | OV2640 SVGA 800×600, JPEG q12, doble buffer en PSRAM, flash | — |
| `firmware/residata_nodo/camara.h` | Interfaz de captura / liberación de buffer | — |
| `firmware/residata_nodo/config.h` | Pines, resolución, calidad, debounce, `CAM_FLASH_ESTABILIZAR_MS` | **[C]** 02/05/06 |
| `firmware/residata_nodo/residata_nodo.ino` | Máquina de estados no bloqueante, disparo al detectar residuo, watchdog, LED | **[C]** 02/05/06 |
| `docs/cableado.md` | Conexiones físicas del nodo | **[C]** 06 |
| `docs/pruebas_hardware.md` | Checklist de validación en placa | **[C]** 02/06 |
| `README.md` | Descripción del proyecto y backlog | **[B]** |
| `firmware/residata_nodo/.gitignore` | Ignora `secrets.h` y builds | **[B]** |

Cobertura de las tareas pedidas:
- Sensor con interrupción por hardware → `sensor.cpp` (`attachInterrupt`, `IRAM_ATTR`).
- Cámara con resolución/calidad configuradas → `config.h` + `camara.cpp`.
- Debounce y disparo al detectar residuo → `sensor.cpp` (150 ms) + `.ino` (`REPOSO → CAPTURANDO`).
- Memoria temporal de la imagen → `camera_fb_t *fbEnCurso` en el `.ino` + `camaraLiberarBuffer()`.
- Latencia < 1 s → `CAM_FLASH_ESTABILIZAR_MS = 80`, `fb_count = 2`, `CAMERA_GRAB_LATEST`.

### HU-02_Transmision-Imagen-API
Responsable: por asignar · Prioridad: Alta

| Archivo | Tarea técnica | Marca |
| --- | --- | --- |
| `firmware/residata_nodo/red.cpp` | Wi-Fi STA, multipart manual, 3 reintentos con backoff 500/1000/2000 ms, timeouts 5 s/8 s, valida HTTP 200 | — |
| `firmware/residata_nodo/red.h` | Contrato `RespuestaClasificacion` | **[C]** 05 |
| `firmware/residata_nodo/secrets.h.example` | Plantilla de SSID, contraseña, host, puerto y API key | **[C]** 01 |
| `docs/instalacion_firmware.md` | Compilación y carga en Arduino IDE | — |

### HU-03_Recepcion-Validacion-Backend
Responsable: por asignar · Prioridad: Alta

| Archivo | Tarea técnica | Marca |
| --- | --- | --- |
| `backend/app/api/v1/dispositivo.py` | `POST /api/v1/dispositivo/clasificar`, `X-Api-Key`, whitelist de extensión, rechazo de vacío | — |
| `backend/app/schemas/dispositivo.py` | Contrato JSON de respuesta al nodo | **[C]** 05 |
| `backend/app/services/almacenamiento.py` | Validación de tamaño (5 MB) y guardado temporal en disco | **[C]** 07 |
| `backend/app/core/deps.py` | Dependencias `SesionBd`, `UsuarioActual`, `ContenedorIoT` | **[C]** 08/09/10 |
| `backend/app/core/seguridad.py` | Hash SHA-256 de API key, JWT, contraseñas | **[C]** 08 |
| `backend/app/core/excepciones.py` | Errores 400/401/403/404/409/413 con JSON uniforme | **[C]** 05/09 |
| `backend/app/main.py` | Arranque FastAPI, CORS, routers, lifespan | **[B] [C]** todas |
| `backend/app/api/v1/router.py` | Agregador de routers v1 | **[B] [C]** 08/09/10 |
| `backend/app/core/config.py` | Configuración central (umbral, storage, JWT, CORS) | **[B] [C]** 04/05/07 |
| `backend/app/core/logging.py` | Logging consola/JSON | **[B]** |
| `backend/app/__init__.py` | Paquete | **[B]** |
| `backend/app/api/__init__.py` | Paquete | **[B]** |
| `backend/app/api/v1/__init__.py` | Paquete | **[B]** |
| `backend/app/core/__init__.py` | Paquete | **[B]** |
| `backend/app/schemas/__init__.py` | Paquete | **[B]** |
| `backend/app/services/__init__.py` | Paquete | **[B]** |
| `backend/app/db/__init__.py` | Paquete | **[B]** |
| `backend/app/db/base.py` | `Base` declarativa de SQLAlchemy | **[B]** |
| `backend/app/db/sesion.py` | Motor, pool, `FabricaSesiones`, `obtener_db` | **[B] [C]** 08/09/10 |
| `backend/app/schemas/comun.py` | `RespuestaPaginada` y helper | **[B] [C]** 09/10 |
| `backend/app/schemas/historico.py` | DTO de clasificación | **[B] [C]** 05/07/08/10 |
| `backend/app/api/v1/salud.py` | `GET /health` | **[?]** |
| `backend/app/api/v1/auth.py` | Login / refresh / me (JWT) | **[?]** |
| `backend/app/api/v1/usuarios.py` | CRUD de usuarios | **[?]** |
| `backend/app/schemas/usuario.py` | DTO de usuario | **[?]** |
| `backend/app/schemas/auth.py` | DTO de tokens | **[?]** |
| `backend/app/schemas/rol.py` | DTO de rol | **[?]** |
| `backend/app/services/usuarios.py` | Servicio de usuarios | **[?]** |
| `backend/app/api/v1/contenedores.py` | CRUD de contenedores y API keys | **[?]** |
| `backend/app/schemas/contenedor.py` | DTO de contenedor | **[?]** |
| `backend/app/services/contenedores.py` | Servicio de contenedores | **[?]** |
| `backend/app/api/v1/catalogos.py` | `GET /roles`, `GET /categorias` | **[?]** |
| `backend/app/schemas/categoria.py` | DTO de categoría | **[?]** |
| `backend/scripts/crear_admin.py` | Bootstrap del administrador | **[?]** |
| `backend/requirements.txt` | Dependencias de ejecución | **[B]** |
| `backend/.env.example` | Variables de entorno de ejemplo | **[B]** |
| `backend/.gitignore` | Ignora `.env`, venv, storage, pesos | **[B]** |
| `backend/storage/imagenes/.gitkeep` | Carpeta de capturas | **[B]** |

### HU-04_Modelo-IA
Responsable: por asignar · Prioridad: Alta

| Archivo | Tarea técnica | Marca |
| --- | --- | --- |
| `backend/app/services/ia_yolo.py` | Carga perezosa de YOLO, preprocesamiento PIL, 3 categorías, confianza, tiempo de inferencia, modo simulado | — |
| `backend/app/ml/README.md` | Ubicación de los pesos | — |
| `backend/app/ml/__init__.py` | Paquete | — |
| `backend/app/ml/pesos/.gitkeep` | Carpeta de pesos | — |
| `backend/requirements-ml.txt` | `ultralytics`, `opencv-python` | **[B]** |

### HU-05_Reglas-Clasificacion
Responsable: por asignar · Prioridad: Alta

| Archivo | Tarea técnica | Marca |
| --- | --- | --- |
| `backend/app/services/procesamiento.py` | Umbral de confianza, fallback a `Peligroso`, categoría → ángulo (`reglas_servo`), respuesta 200 | **[C]** 03/07/08/09 |

> **Aviso:** es el único archivo exclusivo de esta HU. Las reglas también viven en archivos ya
> entregados antes: `core/config.py` (`umbral_confianza`, `categoria_baja_confianza`),
> `db/modelos.py` (`ReglaServo`), `database/02_datos_iniciales.sql` (ángulos 0/90/180) y
> `schemas/dispositivo.py`. Ver decisión 3 en §6.

### HU-06_Servomotor-SG90
Responsable: por asignar · Prioridad: Media

| Archivo | Tarea técnica | Marca |
| --- | --- | --- |
| `firmware/residata_nodo/servo_ctrl.cpp` | `ESP32Servo`, 50 Hz, 500–2400 µs, reserva LEDC 2/3, reposo 90° | — |
| `firmware/residata_nodo/servo_ctrl.h` | Interfaz del servo | — |

> La temporización no bloqueante de 3 s y el regreso a 90° están en `residata_nodo.ino`
> (`ESPERA_CAIDA`, `REGRESANDO`, `TIEMPO_ESPERA_CAIDA_MS`) y `config.h`, entregados en HU-01.

### HU-07_Persistencia-Historicos
Responsable: por asignar · Prioridad: Alta

| Archivo | Tarea técnica | Marca |
| --- | --- | --- |
| `database/01_esquema.sql` | Tabla `historico_clasificaciones`, alertas, catálogos, índices, vista | — |
| `database/02_datos_iniciales.sql` | Roles, categorías, `reglas_servo`, configuración | — |
| `database/04_rollback.sql` | Reversión del esquema | — |
| `database/README.md` | Orden de ejecución | — |
| `backend/app/db/modelos.py` | Entidades SQLAlchemy 2.0 y vista `vw_historico_detalle` | **[C]** 03/05/08/09/10 |
| `backend/alembic.ini` | Configuración de migraciones | — |
| `backend/alembic/env.py` | Entorno Alembic | — |
| `backend/alembic/script.py.mako` | Plantilla de migración | — |
| `backend/alembic/versions/0001_esquema_inicial.py` | Migración del esquema | — |
| `backend/alembic/versions/0002_datos_iniciales.py` | Migración de datos iniciales | — |
| `backend/tests/__init__.py` | Paquete de pruebas | — |
| `backend/tests/test_api_integracion.py` | Pruebas de integración (ingesta, histórico, alertas, dashboard) | — |
| `backend/requirements-dev.txt` | `pytest`, `httpx` | **[B]** |
| `docs/diagrama_er.md` | Diagrama entidad-relación | **[C]** 10 |
| `docs/diccionario_datos.md` | Diccionario de datos | **[C]** 10 |

> `modelos.py` es la entidad de esta HU, pero **HU-03 lo necesita** para autenticar el contenedor.
> Ver decisión 3 en §6.

### HU-08_Dashboard-Tiempo-Real
Responsable: por asignar · Prioridad: Alta

| Archivo | Tarea técnica | Marca |
| --- | --- | --- |
| `backend/app/api/v1/ws.py` | `/api/v1/ws?token=`, valida JWT | — |
| `backend/app/services/tiempo_real.py` | Gestor de conexiones y difusión entre hilos | — |
| `backend/app/api/v1/dashboard.py` | `GET /dashboard/resumen` | **[?]** |
| `backend/app/schemas/dashboard.py` | DTO del resumen | **[?]** |
| `backend/app/services/dashboard.py` | Agregaciones KPIs, categorías, 7 días, últimas | **[?]** |
| `frontend/package.json` | Dependencias y scripts | **[B]** |
| `frontend/package-lock.json` | Lockfile | **[B]** |
| `frontend/tsconfig.json` | TypeScript | **[B]** |
| `frontend/vite.config.ts` | Vite + Tailwind + alias `#lib` | **[B]** |
| `frontend/.npmrc` | Config npm | **[B]** |
| `frontend/.env.example` | Variables Vite de ejemplo | **[B]** |
| `frontend/.gitignore` | Ignora `node_modules`, `.svelte-kit`, `build` | **[B]** |
| `frontend/README.md` | Documentación del frontend | **[B]** |
| `frontend/.vscode/extensions.json` | Extensiones recomendadas | **[B]** |
| `frontend/src/app.html` | Shell HTML | **[B]** |
| `frontend/src/app.d.ts` | Tipos de SvelteKit | **[B]** |
| `frontend/src/lib/config.ts` | `API_URL`, `WS_URL`, `USAR_MOCK`, `SONIDO_ALERTAS` | **[B] [C]** 09/10 |
| `frontend/src/lib/index.ts` | Barrel | **[B]** |
| `frontend/src/lib/tipos/index.ts` | Contratos TypeScript del dominio | **[B] [C]** 09/10 |
| `frontend/src/lib/api/cliente.ts` | Cliente HTTP, errores, expiración de sesión | **[B] [C]** 09/10 |
| `frontend/src/lib/api/index.ts` | Barrel de la capa API | **[B]** |
| `frontend/src/lib/api/auth.ts` | Cliente de autenticación | **[?]** |
| `frontend/src/lib/api/usuarios.ts` | Cliente de usuarios | **[?]** |
| `frontend/src/lib/api/contenedores.ts` | Cliente de contenedores | **[?] [C]** 10 |
| `frontend/src/lib/api/catalogos.ts` | Cliente de catálogos | **[?] [C]** 10 |
| `frontend/src/lib/api/almacenamiento.ts` | Persistencia de tokens | **[?]** |
| `frontend/src/lib/api/dashboard.ts` | Cliente del resumen | **[?]** |
| `frontend/src/lib/api/mock.ts` | Backend simulado y flujo WS simulado | **[B] [C]** 09/10 |
| `frontend/src/lib/stores/sesion.svelte.ts` | Sesión JWT | **[?]** |
| `frontend/src/lib/stores/conexion.svelte.ts` | Estado de conexión WS | — |
| `frontend/src/lib/stores/tiempoReal.ts` | Cliente WS con reconexión exponencial | — |
| `frontend/src/lib/util/formato.ts` | Formatos, colores y variantes | **[B] [C]** 09/10 |
| `frontend/src/lib/components/Boton.svelte` | Botón | **[B]** |
| `frontend/src/lib/components/Tarjeta.svelte` | Tarjeta | **[B]** |
| `frontend/src/lib/components/Cargando.svelte` | Spinner | **[B]** |
| `frontend/src/lib/components/EstadoVacio.svelte` | Estado vacío | **[B]** |
| `frontend/src/lib/components/Insignia.svelte` | Badge | **[B]** |
| `frontend/src/lib/components/CampoSelect.svelte` | Select de formulario | **[B]** |
| `frontend/src/lib/components/CampoTexto.svelte` | Input de formulario | **[B]** |
| `frontend/src/lib/components/Modal.svelte` | Modal | **[B]** |
| `frontend/src/lib/components/Sidebar.svelte` | Navegación lateral | **[B]** |
| `frontend/src/lib/components/Navbar.svelte` | Barra superior + indicador WS | **[C]** 09 |
| `frontend/src/lib/components/Grafica.svelte` | Wrapper Chart.js | **[?]** |
| `frontend/src/lib/components/TablaReciente.svelte` | Últimas clasificaciones | **[?]** |
| `frontend/src/lib/components/TarjetaMetrica.svelte` | Tarjeta KPI | **[?]** |
| `frontend/src/lib/assets/favicon.svg` | Icono | **[B]** |
| `frontend/static/favicon.svg` | Icono público | **[B]** |
| `frontend/static/robots.txt` | Robots | **[B]** |
| `frontend/src/routes/+layout.svelte` | Layout raíz (monta `<Toast/>`) | **[B] [C]** 09 |
| `frontend/src/routes/+layout.ts` | SPA (`ssr=false`) | **[B]** |
| `frontend/src/routes/+page.svelte` | Redirección | **[B]** |
| `frontend/src/routes/+page.ts` | Redirección a `/dashboard` | **[B]** |
| `frontend/src/routes/+error.svelte` | Página de error | **[B]** |
| `frontend/src/routes/login/+page.svelte` | Login | **[?]** |
| `frontend/src/routes/login/+page.ts` | Guard del login | **[?]** |
| `frontend/src/routes/(panel)/+layout.svelte` | Conecta WS y alertas con sesión activa | **[C]** 09 |
| `frontend/src/routes/(panel)/dashboard/+page.svelte` | KPIs y últimas clasificaciones en vivo | **[?]** |
| `frontend/src/routes/(panel)/usuarios/+page.svelte` | Gestión de usuarios | **[?]** |
| `frontend/src/routes/(panel)/contenedores/+page.svelte` | Gestión de contenedores | **[?]** |

### HU-09_Notificacion-Peligrosos
Responsable: por asignar · Prioridad: Alta

| Archivo | Tarea técnica | Marca |
| --- | --- | --- |
| `backend/app/api/v1/alertas.py` | `GET /alertas`, `PATCH /alertas/{id}` | — |
| `backend/app/schemas/alerta.py` | Payload `AlertaLeer` / `AlertaActualizar` | **[C]** 05 |
| `frontend/src/lib/stores/alertas.svelte.ts` | Alertas pendientes, evento `alerta_peligroso`, sonido | — |
| `frontend/src/lib/stores/toast.svelte.ts` | Store de toasts (tipo `peligro`) | **[C]** 08/10 |
| `frontend/src/lib/components/Toast.svelte` | Toast/snackbar con variante roja | — |
| `frontend/src/routes/(panel)/alertas/+page.svelte` | Listado, filtros, atender, sonido | — |
| `frontend/src/lib/api/alertas.ts` | Cliente REST de alertas | — |
| `frontend/src/lib/util/sonido.ts` | Aviso sonoro | — |
| `frontend/src/app.css` | Paleta `--color-peligro-*` (rojo exclusivo) | **[C]** 08/10 |

### HU-10_Reportes-Filtrado
Responsable: por asignar · Prioridad: Media

| Archivo | Tarea técnica | Marca |
| --- | --- | --- |
| `backend/app/api/v1/historico.py` | `GET /api/v1/historico` con filtros y paginación | — |
| `database/03_consultas_dashboard.sql` | Consultas de métricas y reportes | **[C]** dashboard |
| `frontend/src/routes/(panel)/historico/+page.svelte` | Formulario de filtros, tabla, paginación, CSV | — |
| `frontend/src/lib/api/historico.ts` | Cliente REST del histórico | — |
| `frontend/src/lib/util/csv.ts` | Exportación CSV | — |

---

## 4. Base del proyecto

### 4.1 Resumen: qué archivo de base va en qué HU

| Archivo de base | HU destino | Motivo |
| --- | --- | --- |
| `README.md` | HU-01 | Primera entrega; describe todo el proyecto |
| `firmware/residata_nodo/.gitignore` | HU-01 | Necesario desde el primer firmware |
| `backend/.env.example` | HU-03 | Configuración del backend |
| `backend/.gitignore` | HU-03 | Evita `.env`, venv y storage |
| `backend/requirements.txt` | HU-03 | Dependencias de ejecución |
| `backend/app/__init__.py` y `__init__.py` de subpaquetes | HU-03 | Paquetes Python |
| `backend/app/main.py` | HU-03 | Punto de entrada |
| `backend/app/api/v1/router.py` | HU-03 | Agregador de routers |
| `backend/app/core/config.py` | HU-03 | Configuración central |
| `backend/app/core/logging.py` | HU-03 | Logging |
| `backend/app/db/base.py`, `db/sesion.py` | HU-03 | Infraestructura de datos |
| `backend/app/schemas/comun.py`, `schemas/historico.py` | HU-03 | DTOs base |
| `backend/storage/imagenes/.gitkeep` | HU-03 | Carpeta de capturas |
| `backend/requirements-dev.txt` | HU-07 | Pruebas |
| `backend/requirements-ml.txt` | HU-04 | Dependencias de IA |
| `frontend/package.json`, `package-lock.json`, `tsconfig.json`, `vite.config.ts`, `.npmrc` | HU-08 | Toolchain |
| `frontend/.env.example`, `.gitignore`, `README.md`, `.vscode/extensions.json` | HU-08 | Configuración |
| `frontend/src/app.html`, `app.d.ts` | HU-08 | Shell SvelteKit |
| `frontend/src/lib/config.ts`, `lib/index.ts`, `lib/tipos/index.ts` | HU-08 | Base de la SPA |
| `frontend/src/lib/api/cliente.ts`, `api/index.ts` | HU-08 | Cliente HTTP |
| `frontend/src/lib/util/formato.ts` | HU-08 | Formatos y colores |
| UI kit (`Boton`, `Tarjeta`, `Cargando`, `EstadoVacio`, `Insignia`, `CampoSelect`, `CampoTexto`, `Modal`, `Sidebar`) | HU-08 | Componentes reutilizables |
| `frontend/src/lib/assets/*`, `frontend/static/*` | HU-08 | Assets |
| Rutas shell (`+layout`, `+layout.ts`, `+page`, `+page.ts`, `+error`) | HU-08 | Shell de la SPA |
| `frontend/src/app.css` | HU-09 | Tema Tailwind; el rojo es requisito de HU-09 |

### 4.2 Reglas de la Base

- La Base **no genera una entrega aparte**: se copia dentro de la HU indicada, conservando la estructura.
- En el `ENTREGA.md` de esa HU se marca cada archivo como `[Base]`.
- Si una HU posterior necesita un archivo de Base ya copiado, se documenta como dependencia (regla 7).

### 4.3 Archivos compartidos

| Archivo | HUs | Se copia en |
| --- | --- | --- |
| `firmware/residata_nodo/config.h` | 01, 02, 05, 06 | HU-01 |
| `firmware/residata_nodo/residata_nodo.ino` | 01, 02, 05, 06 | HU-01 |
| `firmware/residata_nodo/red.h` | 02, 05 | HU-02 |
| `firmware/residata_nodo/secrets.h.example` | 01, 02 | HU-02 |
| `docs/cableado.md` | 01, 06 | HU-01 |
| `docs/pruebas_hardware.md` | 01, 02, 06 | HU-01 |
| `docs/diagrama_er.md`, `docs/diccionario_datos.md` | 07, 10 | HU-07 |
| `database/03_consultas_dashboard.sql` | 10 + dashboard | HU-10 |
| `backend/app/main.py` | todas | HU-03 |
| `backend/app/api/v1/router.py` | 03, 08, 09, 10 | HU-03 |
| `backend/app/core/config.py` | 03, 04, 05, 07 | HU-03 |
| `backend/app/core/deps.py` | 03, 08, 09, 10 | HU-03 |
| `backend/app/core/seguridad.py` | 03, 08 | HU-03 |
| `backend/app/core/excepciones.py` | 03, 05, 09 | HU-03 |
| `backend/app/db/sesion.py` | 03, 08, 09, 10 | HU-03 |
| `backend/app/db/modelos.py` | 03, 05, 07, 08, 09, 10 | HU-07 (a confirmar) |
| `backend/app/schemas/comun.py` | 03, 09, 10 | HU-03 |
| `backend/app/schemas/historico.py` | 03, 05, 07, 08, 10 | HU-03 |
| `backend/app/schemas/dispositivo.py` | 03, 05 | HU-03 |
| `backend/app/schemas/alerta.py` | 05, 09 | HU-09 |
| `backend/app/services/almacenamiento.py` | 03, 07 | HU-03 |
| `backend/app/services/procesamiento.py` | 03, 05, 07, 08, 09 | HU-05 |
| `frontend/src/lib/config.ts` | 08, 09, 10 | HU-08 |
| `frontend/src/lib/tipos/index.ts` | 08, 09, 10 | HU-08 |
| `frontend/src/lib/api/cliente.ts` | 08, 09, 10 | HU-08 |
| `frontend/src/lib/api/mock.ts` | 08, 09, 10 | HU-08 |
| `frontend/src/lib/api/catalogos.ts`, `api/contenedores.ts` | 08, 10 | HU-08 |
| `frontend/src/lib/util/formato.ts` | 08, 09, 10 | HU-08 |
| `frontend/src/lib/stores/toast.svelte.ts` | 08, 09, 10 | HU-09 |
| `frontend/src/app.css` | 08, 09, 10 | HU-09 |
| `frontend/src/routes/+layout.svelte` | 08, 09 | HU-08 |
| `frontend/src/routes/(panel)/+layout.svelte` | 08, 09 | HU-08 |
| `frontend/src/lib/components/Navbar.svelte` | 08, 09 | HU-08 |

### 4.4 Archivos sin HU propia en el backlog

Estas funciones existen en la app pero **no corresponden a ninguna de las 10 HU**. Se incluyen para
que el panel funcione y se entregan junto a la HU indicada:

| Grupo | Archivos | Se entrega en |
| --- | --- | --- |
| Autenticación (JWT) | `api/v1/auth.py`, `schemas/auth.py`, `api/auth.ts`, `stores/sesion.svelte.ts`, `routes/login/*` | HU-03 (backend) / HU-08 (frontend) |
| Usuarios y roles | `api/v1/usuarios.py`, `schemas/usuario.py`, `schemas/rol.py`, `services/usuarios.py`, `api/usuarios.ts`, `routes/(panel)/usuarios/*` | HU-03 / HU-08 |
| Contenedores | `api/v1/contenedores.py`, `schemas/contenedor.py`, `services/contenedores.py`, `api/contenedores.ts`, `routes/(panel)/contenedores/*` | HU-03 / HU-08 |
| Catálogos | `api/v1/catalogos.py`, `schemas/categoria.py`, `api/catalogos.ts` | HU-03 / HU-08 |
| Salud | `api/v1/salud.py` | HU-03 |
| Bootstrap admin | `scripts/crear_admin.py` | HU-03 |
| Dashboard (agregados) | `api/v1/dashboard.py`, `schemas/dashboard.py`, `services/dashboard.py`, `api/dashboard.ts`, `components/Grafica.svelte`, `components/TablaReciente.svelte`, `components/TarjetaMetrica.svelte`, `routes/(panel)/dashboard/+page.svelte` | HU-08 |
| Almacenamiento de sesión | `api/almacenamiento.ts` | HU-08 |

---

## 5. Archivos que NO se copian

| Archivo | Motivo |
| --- | --- |
| `backend/.env` | Configuración local (ignorada); se copia solo `.env.example` |
| `frontend/.env` | Configuración local (ignorada); se copia solo `.env.example` |
| `firmware/residata_nodo/secrets.h` | Credenciales del nodo (ignorada); se copia solo `secrets.h.example` |
| `backend/storage/imagenes/clasificaciones/2026-10-10/*.jpg` (5) | Capturas de prueba de 8–68 bytes; se copia solo `.gitkeep` |
| `backend/venv/`, `backend/.venv/` | Entornos virtuales |
| `frontend/node_modules/`, `frontend/build/`, `frontend/.svelte-kit/` | Dependencias y build |
| `__pycache__/`, `.pytest_cache/` | Cachés |

---

## 6. Decisiones pendientes (necesito tu confirmación)

1. **Ruta de entregas.** Asumí `C:\Users\victo\OneDrive\Imágenes\ENTREGAS`. ¿Correcta?
2. **Firmware monolítico.** `residata_nodo.ino` incluye `red.h` y `servo_ctrl.h`. La carpeta HU-01
   **no compilará** hasta tener HU-02 y HU-06. ¿Lo aceptamos (recomendado) o quieres el sketch completo
   en HU-01?
3. **`modelos.py`: ¿HU-07 o HU-03?** Propongo HU-07 (es la entidad de persistencia), aceptando que
   HU-03 no arranque sola. Alternativa: adelantarlo a HU-03.
4. **Backend no ejecutable por partes.** `main.py → router.py → 10 routers`; igual que el punto 2.
   ¿Aceptamos carpetas parciales o adelantamos los "hubs" a HU-03?
5. **Funciones sin HU** (auth, usuarios, contenedores, catálogos, dashboard). Propongo incluirlas en la
   Base de HU-03 / HU-08, marcadas `[?]`. Alternativa: una carpeta `HU-11_Panel-Base`.
6. **Discrepancias guía vs código** (no las corrijo, solo aviso):
   - HU-10 pide "paginación de 50": el frontend usa `LIMITE = 15` y el backend `limite=20` por defecto.
   - HU-03 pide "validación MIME/formato JPEG/PNG": solo hay whitelist de extensión y rechazo de vacío;
     no se validan magic bytes ni `content_type`.
   - La guía habla de `Pageable`/`pom.xml` (Java), pero el backend es Python/FastAPI.

---

## 7. Plantilla de `ENTREGA.md` para cada carpeta

```markdown
# HU-XX — <Nombre>

- **ID:** HU-XX
- **Responsable:** <nombre>
- **Prioridad:** <Alta/Media/Baja>
- **Carpeta:** HU-XX_<Nombre>

## Tareas técnicas cubiertas
- <tarea> → <archivo>

## Archivos copiados
| Archivo | Tipo | Origen |
| --- | --- | --- |
| `ruta/relativa` | HU / Base / Compartido | `RESIDATA completo/ruta/relativa` |

## Dependencias de otras HU
- HU-YY: <qué se reutiliza>

## Notas
- <archivos compartidos, limitaciones, credenciales>
```

---

**Esperando tu confirmación de §6 para empezar con `HU-01_Captura-Imagen-Borde`.**
