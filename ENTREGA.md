# HU-07 — Persistencia de Históricos en Base de Datos

- **ID:** HU-07
- **Nombre:** Persistencia de Históricos en Base de Datos
- **Responsable:** Jair
- **Prioridad:** Media
- **Carpeta:** `HU-07_Persistencia-Historicos`
- **Origen:** `RESIDATA completo` (copia íntegra, sin modificar el código)

## Tareas técnicas cubiertas

| Tarea técnica | Archivo(s) | Detalle |
| --- | --- | --- |
| Tabla `historico_clasificaciones` (timestamp, contenedor, categoría, confianza, ángulo, etc.) | `database/01_esquema.sql`, `backend/app/db/modelos.py`, `backend/alembic/versions/0001_esquema_inicial.py` | DDL con PK, FKs, `CHECK` de confianza/ángulo, índices; entidad SQLAlchemy `HistoricoClasificacion` y migración equivalente |
| Entidad ORM del histórico | `backend/app/db/modelos.py` | Modelos SQLAlchemy 2.0: `HistoricoClasificacion`, `CategoriaResiduo`, `Contenedor`, `ReglaServo`, `Alerta`, `Usuario`, `Configuracion`, vista `vw_historico_detalle` |
| "Repositorio" / acceso a datos | `backend/app/db/modelos.py` + `backend/app/db/sesion.py` (HU-03) | El proyecto **no usa patrón Repository**: las consultas se hacen con `Session` + `select()` en los servicios. La sesión y el motor están en `db/sesion.py`, ya entregado en HU-03 |
| Scripts SQL | `database/01_esquema.sql`, `database/02_datos_iniciales.sql`, `database/04_rollback.sql`, `database/README.md` | Esquema completo, datos iniciales (roles, categorías, `reglas_servo` 0/90/180, configuración, contenedores de ejemplo), rollback y guía de ejecución |
| Migraciones | `backend/alembic.ini`, `backend/alembic/env.py`, `backend/alembic/script.py.mako`, `backend/alembic/versions/0001_esquema_inicial.py`, `backend/alembic/versions/0002_datos_iniciales.py` | Alembic; `env.py` toma la URL de `app.core.config` (sin credenciales en el `.ini`) |
| Pruebas de la capa de datos | `backend/tests/test_api_integracion.py`, `backend/tests/__init__.py`, `backend/requirements-dev.txt` | Pruebas de integración con `TestClient` + `pytest` que ejercitan la persistencia a través de la API (ingesta, histórico, alertas, dashboard, usuarios, contenedores) |
| Documentación del modelo de datos | `docs/diagrama_er.md`, `docs/diccionario_datos.md` | Diagrama entidad-relación y diccionario de datos |

### Avisos

- **No hay "repositorio" como clase:** el backend es FastAPI + SQLAlchemy 2 y usa `Session`/`select()` directamente en los servicios. No se creó ni se modificó nada.
- **Las pruebas no son unitarias puras:** `test_api_integracion.py` es el **único** archivo de pruebas del proyecto y valida el flujo completo por HTTP. No hay pruebas unitarias aisladas del repositorio/entidades.
- **`database/03_consultas_dashboard.sql` no va aquí:** el mapa lo asigna a HU-10.

## Archivos copiados

| Archivo | Tipo | Origen |
| --- | --- | --- |
| `database/01_esquema.sql` | HU-07 | `RESIDATA completo/database/01_esquema.sql` |
| `database/02_datos_iniciales.sql` | HU-07 | `RESIDATA completo/database/02_datos_iniciales.sql` |
| `database/04_rollback.sql` | HU-07 | `RESIDATA completo/database/04_rollback.sql` |
| `database/README.md` | HU-07 | `RESIDATA completo/database/README.md` |
| `backend/app/db/modelos.py` | HU-07 (compartido con HU-03/05/08/09/10) | `RESIDATA completo/backend/app/db/modelos.py` |
| `backend/alembic.ini` | HU-07 | `RESIDATA completo/backend/alembic.ini` |
| `backend/alembic/env.py` | HU-07 | `RESIDATA completo/backend/alembic/env.py` |
| `backend/alembic/script.py.mako` | HU-07 | `RESIDATA completo/backend/alembic/script.py.mako` |
| `backend/alembic/versions/0001_esquema_inicial.py` | HU-07 | `RESIDATA completo/backend/alembic/versions/0001_esquema_inicial.py` |
| `backend/alembic/versions/0002_datos_iniciales.py` | HU-07 | `RESIDATA completo/backend/alembic/versions/0002_datos_iniciales.py` |
| `backend/tests/__init__.py` | HU-07 | `RESIDATA completo/backend/tests/__init__.py` |
| `backend/tests/test_api_integracion.py` | HU-07 | `RESIDATA completo/backend/tests/test_api_integracion.py` |
| `backend/requirements-dev.txt` | Base (dependencias de pruebas) | `RESIDATA completo/backend/requirements-dev.txt` |
| `docs/diagrama_er.md` | HU-07 (compartido con HU-10) | `RESIDATA completo/docs/diagrama_er.md` |
| `docs/diccionario_datos.md` | HU-07 (compartido con HU-10) | `RESIDATA completo/docs/diccionario_datos.md` |

**Total: 15 archivos**, todos verificados byte a byte contra el origen.

## Dependencias de otras HU

| HU | Qué se reutiliza |
| --- | --- |
| **HU-03 (obligatoria)** | `backend/app/core/config.py` (`DATABASE_URL`), `backend/app/db/sesion.py` (motor, pool, `obtener_db`), `backend/app/db/base.py` (`Base`), `backend/requirements.txt`, `backend/.env.example` |
| **HU-04** | No requerida para esta entrega, pero `0002_datos_iniciales` no depende de ella |
| **HU-05** | `services/procesamiento.py` consume `HistoricoClasificacion`, `ReglaServo` y `CategoriaResiduo` |
| **HU-08/09/10** | Consumen `modelos.py` (dashboard, alertas, histórico) |

- **Consecuencia:** las migraciones y entidades **no se ejecutan aisladas**; necesitan la configuración y
  la sesión de HU-03 y una base PostgreSQL accesible.

## Credenciales

- **No se copió ningún `.env` real** (no forma parte de esta HU).
- `backend/alembic.ini` deja `sqlalchemy.url` **vacía** y `env.py` inyecta `DATABASE_URL` desde la
  configuración: **sin credenciales en el archivo**.
- `database/README.md` usa el placeholder `PGPASSWORD = "TU_CONTRASENA"`; **no es una contraseña real**.
- `database/02_datos_iniciales.sql` inserta `api_key_hash` de ejemplo con valores ficticios
  (`$argon2id$...$seed-hash-contenedor-patio-a` / `...-entrada-b`); **no son claves reales**.
- Las pruebas leen `config.admin_correo` / `config.admin_contrasena` del entorno (valor de ejemplo
  `Cambiar123!` en `.env.example`), **sin credenciales de producción**.

## Notas

- **Archivo compartido:** `modelos.py` es la entidad central de persistencia y lo consumen casi todas
  las HU posteriores; se copia completo aquí (regla 7).
- **`database/03_consultas_dashboard.sql`** pertenece a HU-10, no a esta entrega.
- **Sin Git:** esta entrega se creó solo con copia de archivos; no se ejecutó ningún comando de Git.
- El código se copió **sin modificaciones**; no se refactorizó ni se reformateó nada.
