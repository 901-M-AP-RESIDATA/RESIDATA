# HU-08 — Actualización del Dashboard en Tiempo Real

- **ID:** HU-08
- **Nombre:** Actualización del Dashboard en Tiempo Real
- **Responsable:** Jose M.
- **Prioridad:** Media
- **Carpeta:** `HU-08_Dashboard-Tiempo-Real`
- **Origen:** `RESIDATA completo` (copia íntegra, sin modificar el código)

## Tareas técnicas cubiertas

| Tarea técnica | Archivo(s) | Detalle |
| --- | --- | --- |
| Servidor WebSocket en la aplicación | `backend/app/api/v1/ws.py`, `backend/app/services/tiempo_real.py` | Endpoint `GET /api/v1/ws?token=<JWT>`; valida el token de acceso y el usuario activo; `GestorConexiones` mantiene el set de sockets y difunde de forma segura entre hilos con `run_coroutine_threadsafe()` |
| Cliente WebSocket en la interfaz | `frontend/src/lib/stores/tiempoReal.ts`, `frontend/src/lib/stores/conexion.svelte.ts` | Cliente único con `suscribir()`, conexión a `WS_URL/api/v1/ws?token=...`, reconexión con backoff exponencial (1 s → 15 s) y store de estado (`conectando`/`conectado`/`reconectando`/`desconectado`) |
| Emisión automática del evento tras registrar cada clasificación en BD | `backend/app/services/tiempo_real.py` + `backend/app/services/procesamiento.py` (HU-05) | `procesamiento.py` llama `gestor.difundir({"tipo": "nueva_clasificacion", ...})` y `{"tipo": "alerta_peligroso", ...}` justo después de `db.flush()` / `db.refresh()` |
| Actualización del estado global/local de la UI al recibir la notificación | `frontend/src/routes/(panel)/+layout.svelte`, `frontend/src/lib/stores/conexion.svelte.ts`, `frontend/src/routes/(panel)/dashboard/+page.svelte` | El layout del panel conecta `tiempoReal` y las alertas mientras hay sesión; el dashboard consume los eventos y refresca KPIs y últimas clasificaciones |
| Latencia persistencia → UI < 2 s | `backend/app/services/tiempo_real.py`, `frontend/src/lib/stores/tiempoReal.ts` | Difusión inmediata por el bucle de eventos, sin polling; el cliente marca actividad al recibir cada mensaje (`conexion.marcarActividad()`) |

### Flujo implementado

```
ESP32 → POST /clasificar → procesar_lectura() → db.flush() → gestor.difundir()
                                                                    │
                                    WebSocket /api/v1/ws?token=JWT ──┘
                                                                    │
                        tiempoReal.emitir(evento) → dashboard/alertas (UI)
```

### Avisos sobre la implementación

- **La emisión ocurre tras `flush()`, no tras el `commit`:** el commit lo hace la dependencia
  `obtener_db()` (HU-03) al terminar la petición. El evento puede llegar al cliente antes de que la
  transacción se confirme. No se modificó el código.
- **No hay medición explícita de la latencia < 2 s:** se cumple por diseño (difusión inmediata sin
  polling), pero no existe un cronómetro ni un test que lo verifique.
- **El dashboard no hace polling:** se actualiza con los eventos `nueva_clasificacion` /
  `alerta_peligroso`.

## Archivos copiados

### Backend (5)

| Archivo | Tipo | Origen |
| --- | --- | --- |
| `backend/app/api/v1/ws.py` | HU-08 | `RESIDATA completo/backend/app/api/v1/ws.py` |
| `backend/app/services/tiempo_real.py` | HU-08 | `RESIDATA completo/backend/app/services/tiempo_real.py` |
| `backend/app/api/v1/dashboard.py` | HU-08 (sin HU propia) | `RESIDATA completo/backend/app/api/v1/dashboard.py` |
| `backend/app/schemas/dashboard.py` | HU-08 (sin HU propia) | `RESIDATA completo/backend/app/schemas/dashboard.py` |
| `backend/app/services/dashboard.py` | HU-08 (sin HU propia) | `RESIDATA completo/backend/app/services/dashboard.py` |

### Base del frontend — configuración y raíz (11)

| Archivo | Tipo |
| --- | --- |
| `frontend/package.json` | Base |
| `frontend/package-lock.json` | Base |
| `frontend/tsconfig.json` | Base |
| `frontend/vite.config.ts` | Base |
| `frontend/.npmrc` | Base |
| `frontend/.env.example` | Base |
| `frontend/.gitignore` | Base |
| `frontend/README.md` | Base |
| `frontend/.vscode/extensions.json` | Base |
| `frontend/src/app.html` | Base |
| `frontend/src/app.d.ts` | Base |

### Base del frontend — `src/lib` (16)

| Archivo | Tipo |
| --- | --- |
| `frontend/src/lib/config.ts` | Base (compartido con HU-09/10) |
| `frontend/src/lib/index.ts` | Base |
| `frontend/src/lib/tipos/index.ts` | Base (compartido con HU-09/10) |
| `frontend/src/lib/api/cliente.ts` | Base (compartido con HU-09/10) |
| `frontend/src/lib/api/index.ts` | Base |
| `frontend/src/lib/api/auth.ts` | Base (sin HU propia) |
| `frontend/src/lib/api/usuarios.ts` | Base (sin HU propia) |
| `frontend/src/lib/api/contenedores.ts` | Base (sin HU propia, compartido con HU-10) |
| `frontend/src/lib/api/catalogos.ts` | Base (sin HU propia, compartido con HU-10) |
| `frontend/src/lib/api/almacenamiento.ts` | Base (sin HU propia) |
| `frontend/src/lib/api/dashboard.ts` | Base (sin HU propia) |
| `frontend/src/lib/api/mock.ts` | Base (compartido con HU-09/10) |
| `frontend/src/lib/stores/sesion.svelte.ts` | Base (sin HU propia) |
| `frontend/src/lib/stores/conexion.svelte.ts` | HU-08 |
| `frontend/src/lib/stores/tiempoReal.ts` | HU-08 |
| `frontend/src/lib/util/formato.ts` | Base (compartido con HU-09/10) |

### Base del frontend — componentes (13)

| Archivo | Tipo |
| --- | --- |
| `frontend/src/lib/components/Boton.svelte` | Base |
| `frontend/src/lib/components/Tarjeta.svelte` | Base |
| `frontend/src/lib/components/Cargando.svelte` | Base |
| `frontend/src/lib/components/EstadoVacio.svelte` | Base |
| `frontend/src/lib/components/Insignia.svelte` | Base |
| `frontend/src/lib/components/CampoSelect.svelte` | Base |
| `frontend/src/lib/components/CampoTexto.svelte` | Base |
| `frontend/src/lib/components/Modal.svelte` | Base |
| `frontend/src/lib/components/Sidebar.svelte` | Base |
| `frontend/src/lib/components/Navbar.svelte` | Base (compartido con HU-09) |
| `frontend/src/lib/components/Grafica.svelte` | Base (sin HU propia) |
| `frontend/src/lib/components/TablaReciente.svelte` | Base (sin HU propia) |
| `frontend/src/lib/components/TarjetaMetrica.svelte` | Base (sin HU propia) |

### Assets y estáticos (3)

| Archivo | Tipo |
| --- | --- |
| `frontend/src/lib/assets/favicon.svg` | Base |
| `frontend/static/favicon.svg` | Base |
| `frontend/static/robots.txt` | Base |

### Base del frontend — rutas (11)

| Archivo | Tipo |
| --- | --- |
| `frontend/src/routes/+layout.svelte` | Base (compartido con HU-09) |
| `frontend/src/routes/+layout.ts` | Base |
| `frontend/src/routes/+page.svelte` | Base |
| `frontend/src/routes/+page.ts` | Base |
| `frontend/src/routes/+error.svelte` | Base |
| `frontend/src/routes/login/+page.svelte` | Base (sin HU propia) |
| `frontend/src/routes/login/+page.ts` | Base (sin HU propia) |
| `frontend/src/routes/(panel)/+layout.svelte` | HU-08 (compartido con HU-09) |
| `frontend/src/routes/(panel)/dashboard/+page.svelte` | HU-08 (sin HU propia) |
| `frontend/src/routes/(panel)/usuarios/+page.svelte` | Base (sin HU propia) |
| `frontend/src/routes/(panel)/contenedores/+page.svelte` | Base (sin HU propia) |

**Total: 59 archivos** (5 backend + 54 frontend), todos verificados byte a byte contra el origen.

## Dependencias de otras HU

| HU | Qué se reutiliza |
| --- | --- |
| **HU-03** | `backend/app/core/seguridad.py` (`decodificar_token`), `core/logging.py`, `db/sesion.py` (`FabricaSesiones`, `obtener_db`), `schemas/comun.py` |
| **HU-05** | `backend/app/services/procesamiento.py` es quien emite los eventos con `gestor.difundir()` |
| **HU-07** | `backend/app/db/modelos.py` (`Usuario`, `HistoricoClasificacion`, `CategoriaResiduo`) |
| **HU-09 (necesaria para compilar el frontend)** | `frontend/src/app.css`, `frontend/src/lib/components/Toast.svelte`, `frontend/src/lib/stores/alertas.svelte.ts`, `frontend/src/lib/stores/toast.svelte.ts` |
| **HU-10 (necesaria para compilar el frontend)** | `frontend/src/lib/api/historico.ts` (re-exportado por `api/index.ts`) |

### Imports que quedan sin resolver en esta carpeta

Verificado automáticamente sobre los 54 archivos del frontend:

| Import | Archivo que lo usa | Se entrega en |
| --- | --- | --- |
| `../app.css` | `src/routes/+layout.svelte` | HU-09 |
| `#lib/components/Toast.svelte` | `src/routes/+layout.svelte` | HU-09 |
| `#lib/stores/alertas.svelte.ts` | `src/routes/(panel)/+layout.svelte`, `src/lib/components/Sidebar.svelte` | HU-09 |
| `#lib/stores/toast.svelte.ts` | `src/lib/components/Navbar.svelte`, `(panel)/usuarios/+page.svelte`, `(panel)/contenedores/+page.svelte` | HU-09 |
| `./alertas` | `src/lib/api/index.ts` | HU-09 |
| `./historico` | `src/lib/api/index.ts` | HU-10 |

- **Consecuencia:** el frontend **no compila aislado** hasta tener HU-09 y HU-10. El backend de esta
  HU tampoco arranca sin HU-03/05/07 (router, modelos, procesamiento). Se documenta como dependencia
  hacia adelante, sin modificar código.

## Credenciales

- **No se copió ningún `.env` real**; solo `frontend/.env.example`.
- Revisado `frontend/.env.example`: únicamente `VITE_API_URL=http://localhost:8000`,
  `VITE_USAR_MOCK=false` y `VITE_SONIDO_ALERTAS=true`. **Sin credenciales ni secretos.**

## Notas

- **Entrega más grande del proyecto:** 59 archivos, incluye casi todo el frontend (toolchain, UI kit,
  rutas shell, login, dashboard, usuarios y contenedores) porque el mapa asigna aquí la Base del frontend.
- **Archivos compartidos:** `config.ts`, `tipos/index.ts`, `api/cliente.ts`, `api/mock.ts`,
  `util/formato.ts`, `Navbar.svelte`, `+layout.svelte` y `(panel)/+layout.svelte` sirven también a HU-09/10;
  se copian completos aquí (regla 7).
- **Funciones sin HU propia incluidas:** autenticación, usuarios, contenedores, catálogos y dashboard
  (marcadas `[?]` en el mapa).
- **Sin Git:** esta entrega se creó solo con copia de archivos; no se ejecutó ningún comando de Git.
- El código se copió **sin modificaciones**; no se refactorizó ni se reformateó nada.
