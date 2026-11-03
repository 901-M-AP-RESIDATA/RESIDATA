# HU-03 — Recepción y Validación de Datos en Backend

- **ID:** HU-03
- **Nombre:** Recepción y Validación de Datos en Backend
- **Responsable:** Jair
- **Prioridad:** Alta
- **Carpeta:** `HU-03_Recepcion-Validacion-Backend`
- **Origen:** `RESIDATA completo` (copia íntegra, sin modificar el código)

> **Nota sobre el stack:** el backend de ResiData es **Python 3.12 + FastAPI + SQLAlchemy 2**,
> no Java. Por eso **no existen** `pom.xml`, `build.gradle` ni `application.properties`.
> Sus equivalentes son `backend/requirements.txt`, `backend/app/main.py` y `backend/.env.example`,
> todos incluidos aquí como Base del backend.

## Tareas técnicas cubiertas

| Tarea técnica | Archivo(s) | Detalle |
| --- | --- | --- |
| Controlador REST con el endpoint que recibe la imagen | `backend/app/api/v1/dispositivo.py` | `POST /api/v1/dispositivo/clasificar` con `UploadFile`; autenticación del nodo por cabecera `X-Api-Key` (`ContenedorIoT`); delega en `procesamiento.procesar_lectura()` |
| Validaciones de tipo/formato (JPEG/PNG no vacíos) | `backend/app/api/v1/dispositivo.py`, `backend/app/services/almacenamiento.py` | Rechazo de contenido vacío (`ErrorDatos`), whitelist de extensión `{jpg, jpeg, png, webp}` y límite de tamaño de 5 MB (`TAMANO_MAX_IMAGEN_MB`) |
| Autenticación y autorización de la ingesta | `backend/app/core/deps.py`, `backend/app/core/seguridad.py` | Dependencia `ContenedorIoT` (hash SHA-256 de la API key) y `SesionBd`; JWT y hash de contraseñas |
| Errores uniformes de la API | `backend/app/core/excepciones.py` | 400/401/403/404/409/413 con JSON homogéneo |
| Contrato de respuesta al nodo | `backend/app/schemas/dispositivo.py`, `backend/app/schemas/historico.py` | `RespuestaClasificacion` (categoría, ángulo, confianza, tiempo de inferencia, alerta) |
| Arranque y configuración del backend | `backend/app/main.py`, `backend/app/api/v1/router.py`, `backend/app/core/config.py`, `backend/app/core/logging.py` | FastAPI, CORS, lifespan, agregador de routers v1, configuración central y logging |
| Infraestructura de datos | `backend/app/db/base.py`, `backend/app/db/sesion.py` | `Base` declarativa, motor, pool y `obtener_db` |
| Dependencias y configuración de entorno | `backend/requirements.txt`, `backend/.env.example`, `backend/.gitignore`, `backend/storage/imagenes/.gitkeep` | Dependencias de ejecución, plantilla de variables, exclusiones y carpeta de capturas |

### Sobre la validación MIME (aviso)

La tarea pedía "validación de tipo MIME y formato (JPEG/PNG no vacíos)". El código entregado
**no valida el `Content-Type` ni los magic bytes**: solo comprueba que el archivo no esté vacío,
que no supere 5 MB y que la **extensión** del nombre esté en `{jpg, jpeg, png, webp}`. Si la
extensión no es válida, cae por defecto en `"jpg"`. Esto se documenta como discrepancia; **no se
modificó el código**.

## Archivos copiados

### Archivos propios de la HU

| Archivo | Tipo | Origen |
| --- | --- | --- |
| `backend/app/api/v1/dispositivo.py` | HU-03 | `RESIDATA completo/backend/app/api/v1/dispositivo.py` |
| `backend/app/services/almacenamiento.py` | HU-03 (compartido con HU-07) | `.../backend/app/services/almacenamiento.py` |
| `backend/app/core/deps.py` | HU-03 (compartido con HU-08/09/10) | `.../backend/app/core/deps.py` |
| `backend/app/core/seguridad.py` | HU-03 (compartido con HU-08) | `.../backend/app/core/seguridad.py` |
| `backend/app/core/excepciones.py` | HU-03 (compartido con HU-05/09) | `.../backend/app/core/excepciones.py` |
| `backend/app/schemas/dispositivo.py` | HU-03 (compartido con HU-05) | `.../backend/app/schemas/dispositivo.py` |
| `backend/app/api/v1/salud.py` | HU-03 (sin HU propia) | `.../backend/app/api/v1/salud.py` |
| `backend/app/api/v1/auth.py` | HU-03 (sin HU propia) | `.../backend/app/api/v1/auth.py` |
| `backend/app/schemas/auth.py` | HU-03 (sin HU propia) | `.../backend/app/schemas/auth.py` |
| `backend/app/api/v1/usuarios.py` | HU-03 (sin HU propia) | `.../backend/app/api/v1/usuarios.py` |
| `backend/app/schemas/usuario.py` | HU-03 (sin HU propia) | `.../backend/app/schemas/usuario.py` |
| `backend/app/schemas/rol.py` | HU-03 (sin HU propia) | `.../backend/app/schemas/rol.py` |
| `backend/app/services/usuarios.py` | HU-03 (sin HU propia) | `.../backend/app/services/usuarios.py` |
| `backend/app/api/v1/contenedores.py` | HU-03 (sin HU propia) | `.../backend/app/api/v1/contenedores.py` |
| `backend/app/schemas/contenedor.py` | HU-03 (sin HU propia) | `.../backend/app/schemas/contenedor.py` |
| `backend/app/services/contenedores.py` | HU-03 (sin HU propia) | `.../backend/app/services/contenedores.py` |
| `backend/app/api/v1/catalogos.py` | HU-03 (sin HU propia) | `.../backend/app/api/v1/catalogos.py` |
| `backend/app/schemas/categoria.py` | HU-03 (sin HU propia) | `.../backend/app/schemas/categoria.py` |
| `backend/scripts/crear_admin.py` | HU-03 (sin HU propia) | `.../backend/scripts/crear_admin.py` |

### Base del backend

| Archivo | Tipo | Origen |
| --- | --- | --- |
| `backend/app/main.py` | Base (compartido con todas) | `.../backend/app/main.py` |
| `backend/app/api/v1/router.py` | Base (compartido con HU-08/09/10) | `.../backend/app/api/v1/router.py` |
| `backend/app/core/config.py` | Base (compartido con HU-04/05/07) | `.../backend/app/core/config.py` |
| `backend/app/core/logging.py` | Base | `.../backend/app/core/logging.py` |
| `backend/app/db/base.py` | Base | `.../backend/app/db/base.py` |
| `backend/app/db/sesion.py` | Base (compartido con HU-08/09/10) | `.../backend/app/db/sesion.py` |
| `backend/app/schemas/comun.py` | Base (compartido con HU-09/10) | `.../backend/app/schemas/comun.py` |
| `backend/app/schemas/historico.py` | Base (compartido con HU-05/07/08/10) | `.../backend/app/schemas/historico.py` |
| `backend/app/__init__.py` | Base | `.../backend/app/__init__.py` |
| `backend/app/api/__init__.py` | Base | `.../backend/app/api/__init__.py` |
| `backend/app/api/v1/__init__.py` | Base | `.../backend/app/api/v1/__init__.py` |
| `backend/app/core/__init__.py` | Base | `.../backend/app/core/__init__.py` |
| `backend/app/db/__init__.py` | Base | `.../backend/app/db/__init__.py` |
| `backend/app/schemas/__init__.py` | Base | `.../backend/app/schemas/__init__.py` |
| `backend/app/services/__init__.py` | Base | `.../backend/app/services/__init__.py` |
| `backend/requirements.txt` | Base | `.../backend/requirements.txt` |
| `backend/.env.example` | Base | `.../backend/.env.example` |
| `backend/.gitignore` | Base | `.../backend/.gitignore` |
| `backend/storage/imagenes/.gitkeep` | Base | `.../backend/storage/imagenes/.gitkeep` |

**Total: 38 archivos** (19 propios + 19 de Base), todos verificados byte a byte contra el origen.

## Dependencias de otras HU

- **Previas:** ninguna. HU-03 es la primera entrega del backend.
- **Posteriores necesarias para que el backend arranque completo:**
  - **HU-04:** `backend/app/services/ia_yolo.py` (usado por `procesamiento.py`).
  - **HU-05:** `backend/app/services/procesamiento.py` — `dispositivo.py` lo importa directamente.
  - **HU-07:** `backend/app/db/modelos.py` — `deps.py` importa `Contenedor` y `Usuario`; sin él, el backend no importa.
  - **HU-08/09/10:** `backend/app/api/v1/dashboard.py`, `alertas.py`, `historico.py`, `ws.py` — `router.py` los importa todos.
- **Consecuencia:** esta carpeta **no es ejecutable de forma aislada**; se entrega como el módulo de ingesta y su base. Se documenta como dependencia hacia adelante, sin modificar código.

## Credenciales

- **No se copió ningún `.env` real.** Solo `backend/.env.example`.
- Revisado `backend/.env.example`: contiene únicamente **valores de ejemplo/local** —
  `DATABASE_URL=postgresql+psycopg://postgres:postgres@127.0.0.1:5432/residata`,
  `JWT_SECRETO=cambiar-este-secreto-por-uno-aleatorio-de-48-bytes` y
  `ADMIN_CONTRASENA=Cambiar123!`. **No hay credenciales reales ni de producción.**
- Se recomienda cambiar `JWT_SECRETO` y `ADMIN_CONTRASENA` antes de desplegar.

## Notas

- **Archivos compartidos:** `almacenamiento.py`, `deps.py`, `seguridad.py`, `excepciones.py`, `dispositivo.py` (schema), `config.py`, `router.py`, `sesion.py`, `comun.py`, `historico.py` y `main.py` sirven a varias HU. Se copian completos aquí (regla 7).
- **Archivos sin HU propia:** autenticación, usuarios, roles, contenedores, catálogos, salud y bootstrap de admin se incluyen en esta entrega porque el mapa los asigna a HU-03.
- **Discrepancia MIME:** ver aviso arriba; el código solo valida extensión, tamaño y contenido no vacío.
- **Sin Git:** esta entrega se creó solo con copia de archivos; no se ejecutó ningún comando de Git.
- El código se copió **sin modificaciones**; no se refactorizó ni se reformateó nada.
