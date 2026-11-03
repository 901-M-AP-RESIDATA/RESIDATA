# HU-10 — Reportes y Filtrado de Históricos

- **ID:** HU-10
- **Nombre:** Reportes y Filtrado de Históricos
- **Responsable:** Nicole
- **Prioridad:** Baja
- **Carpeta:** `HU-10_Reportes-Filtrado`
- **Origen:** `RESIDATA completo` (copia íntegra, sin modificar el código)
- **Última entrega del proyecto** (incluye la comparación de completitud final)

## Tareas técnicas cubiertas

| Tarea técnica | Archivo(s) | Detalle |
| --- | --- | --- |
| Endpoint `GET /api/v1/historico` con filtros y paginación | `backend/app/api/v1/historico.py` | Router `prefix="/historico"`; filtros `fecha_desde`, `fecha_hasta`, `categoria` (sin distinguir mayúsculas) y `contenedor_id`; paginación por `pagina` (≥ 1) y `limite` (por defecto 20, máx. 1000) traducida a `offset`/`limit`; orden `fecha_hora DESC`; respuesta `RespuestaPaginada[HistoricoClasificacionLeer]` con `total`, `pagina`, `limite`, `paginas` |
| Formulario de filtros | `frontend/src/routes/(panel)/historico/+page.svelte` | Campos «Desde», «Hasta», «Categoría» y «Contenedor»; botones «Buscar» (submit) y «Limpiar»; los catálogos se cargan con `listarCategorias()` y `listarContenedores()` |
| Tabla de resultados | `frontend/src/routes/(panel)/historico/+page.svelte` | Tabla con Fecha y hora, Categoría (insignia por variante), Contenedor, Confianza (%), Tiempo de inferencia y Origen (Automática / Corregida); estados de carga, error y vacío; se antepone en vivo cada `nueva_clasificacion` recibida por WebSocket |
| Exportación CSV | `frontend/src/lib/util/csv.ts`, `frontend/src/routes/(panel)/historico/+page.svelte` | `generarCsv()` (escape de comillas/comas/saltos, CRLF) y `descargarCsv()` (Blob con BOM UTF-8 para Excel); la página pide hasta 1000 registros con los filtros activos y descarga `historico_residata_<marca>.csv` |
| Paginación | `frontend/src/routes/(panel)/historico/+page.svelte`, `backend/app/api/v1/historico.py` | Controles «Anterior» / «Siguiente» y texto «Página X de Y»; indicador «Mostrando inicio–fin de total» |
| Cliente REST del histórico | `frontend/src/lib/api/historico.ts` | `listarHistorico(filtros, signal)` construye el query string (`fecha_desde`, `fecha_hasta`, `categoria`, `contenedor_id`, `pagina`, `limite`) y llama a `http.get` |
| Consultas de métricas y reportes | `database/03_consultas_dashboard.sql` | Script de solo lectura con 7 consultas: residuos por categoría, por día (últimos 30 días), por contenedor, confianza promedio por categoría, clasificaciones de baja confianza, alertas pendientes y últimas 20 lecturas |

### Flujo implementado

```
Formulario (desde / hasta / categoría / contenedor)
        │  Buscar
        ▼
listarHistorico({ ..., pagina, limite }) ──► GET /api/v1/historico
        │                                        │
        │   RespuestaPaginada{items,total,paginas}
        ▼                                        ▼
Tabla de resultados  ◄── items (más reciente primero)
        │
        ├─ Exportar CSV → generarCsv() → descargarCsv()
        └─ Anterior / Siguiente → cambiarPagina()
```

## Avisos sobre la implementación

1. **Paginación distinta a la del enunciado.** El requisito pide **50 registros por página**, pero el
   código entregado usa:
   - frontend: `const LIMITE = 15` en `historico/+page.svelte`;
   - backend: `limite: int = Query(default=20, ge=1, le=1000)` y el cliente `api/historico.ts` usa `?? 20`.

   No se modificó nada; se documenta la discrepancia. Para cumplir el requisito habría que cambiar
   `LIMITE` a 50 (una sola línea, previa autorización).
2. **No hay «Pageable».** El proyecto es **Python/FastAPI + SQLAlchemy**, no Java/Spring: no existen
   `pom.xml`, `build.gradle`, `application.properties` ni `Pageable`. El equivalente funcional es la
   paginación `offset`/`limit` descrita arriba.
3. **La página de históricos no incluye gráfico.** La tabla y los filtros están en
   `historico/+page.svelte`, pero **no hay ningún gráfico** en esa ruta. El único gráfico del proyecto
   (`Grafica.svelte`) está en el **dashboard** y se entrega en **HU-08**. No se añadió ni se inventó
   código para cubrir ese punto.
4. **`database/03_consultas_dashboard.sql` no lo consume la aplicación:** son consultas manuales para
   `psql -f`; el backend usa SQLAlchemy sobre la vista `VistaHistoricoDetalle`.

## Archivos copiados

| Archivo | Tipo | Origen |
| --- | --- | --- |
| `backend/app/api/v1/historico.py` | HU-10 | `RESIDATA completo/backend/app/api/v1/historico.py` |
| `database/03_consultas_dashboard.sql` | HU-10 | `RESIDATA completo/database/03_consultas_dashboard.sql` |
| `frontend/src/lib/api/historico.ts` | HU-10 (compartido con HU-08) | `RESIDATA completo/frontend/src/lib/api/historico.ts` |
| `frontend/src/lib/util/csv.ts` | HU-10 | `RESIDATA completo/frontend/src/lib/util/csv.ts` |
| `frontend/src/routes/(panel)/historico/+page.svelte` | HU-10 | `RESIDATA completo/frontend/src/routes/(panel)/historico/+page.svelte` |

**Total: 5 archivos**, todos verificados byte a byte contra el origen.

## Dependencias de otras HU

| HU | Qué se reutiliza |
| --- | --- |
| **HU-03** | `backend/app/core/deps.py` (`SesionBd`, `UsuarioActual`), `schemas/comun.py` (`RespuestaPaginada`, `construir_paginada`) |
| **HU-07** | `backend/app/db/modelos.py` (`VistaHistoricoDetalle`) y `schemas/historico.py` (`HistoricoClasificacionLeer`) |
| **HU-08** | Base completa del frontend: `api/cliente.ts`, `tipos/index.ts`, `util/formato.ts`, `stores/tiempoReal.ts`, `stores/toast.svelte.ts`, `api/catalogos.ts`, `api/contenedores.ts`, componentes `Boton`, `Cargando`, `EstadoVacio`, `Insignia`, `Tarjeta` y el layout `(panel)/+layout.svelte` |
| **HU-09** | `app.css` (tema Tailwind) y los stores/utilidades de notificación que usa el layout |

- **Consecuencia:** esta carpeta **no compila/arranca aislada**; necesita HU-03/07 en el backend y
  HU-08/09 en el frontend. Se documenta como dependencia, sin modificar código.

## Credenciales

- **No se copió ningún `.env` ni configuración con secretos.** Esta entrega no contiene contraseñas,
  API keys ni tokens.

---

# Comparación final de completitud

Comparación de `RESIDATA completo` contra las 10 carpetas de `ENTREGAS`, excluyendo artefactos de
compilación (`.git`, `venv`, `.venv`, `node_modules`, `build`, `.svelte-kit`, `__pycache__`,
`.pytest_cache`).

| Métrica | Resultado |
| --- | --- |
| Archivos reales de la app (sin artefactos ni `.git`) | **156** |
| Archivos entregados en las 10 HU (sin contar los `ENTREGA.md`) | **148** |
| Archivos de la app **no entregados** | **8** (exclusiones intencionadas) |
| Archivos entregados que **no existen** en la app | **0** |
| Archivos entregados en **más de una HU** | **0** |

### Reparto por HU

| HU | Archivos |
| --- | --- |
| HU-01_Captura-Imagen-Borde | 10 |
| HU-02_Transmision-Imagen-API | 4 |
| HU-03_Recepcion-Validacion-Backend | 38 |
| HU-04_Modelo-IA | 5 |
| HU-05_Reglas-Clasificacion | 1 |
| HU-06_Servomotor-SG90 | 2 |
| HU-07_Persistencia-Historicos | 15 |
| HU-08_Dashboard-Tiempo-Real | 59 |
| HU-09_Notificacion-Peligrosos | 9 |
| HU-10_Reportes-Filtrado | 5 |
| **Total** | **148** |

### Los 8 archivos excluidos (y por qué)

| Archivo | Motivo |
| --- | --- |
| `backend/.env` | Configuración local con credenciales; solo se entrega `.env.example` (HU-03) |
| `frontend/.env` | Configuración local; solo se entrega `.env.example` (HU-08) |
| `firmware/residata_nodo/secrets.h` | Secretos WiFi/API del nodo; solo se entrega `secrets.example.h` (HU-02) |
| `backend/storage/imagenes/clasificaciones/2026-10-10/clasif_20261010194315_7f439763.jpg` | Imagen de prueba generada en ejecución (8–68 bytes) |
| `.../clasif_20261010194401_e3cca9eb.jpg` | Imagen de prueba generada en ejecución |
| `.../clasif_20261010194425_03255c1a.jpg` | Imagen de prueba generada en ejecución |
| `.../clasif_20261010195829_b3b9ebdf.jpg` | Imagen de prueba generada en ejecución |
| `.../clasif_20261010195919_79fd85c4.jpg` | Imagen de prueba generada en ejecución |

**Conclusión:** no falta ningún archivo de la aplicación de forma involuntaria. Las únicas ausencias
son las 3 configuraciones locales con secretos y las 5 imágenes de prueba, todas excluidas a propósito
por las reglas de la entrega.

### README final

El `README.md` raíz del proyecto **está asignado a HU-01** en `MAPA_ENTREGAS.md` (§3, marca `[B]`:
«Primera entrega; describe todo el proyecto»). Por tanto **no se añadió ningún README a HU-10**; ya
viaja en `HU-01_Captura-Imagen-Borde/README.md`.

## Notas

- **Archivo compartido:** `frontend/src/lib/api/historico.ts` lo re-exporta el barrel
  `api/index.ts` de HU-08; se copia completo aquí (regla 7) para que el frontend de HU-08 pueda
  compilar.
- **Sin Git:** esta entrega se creó solo con copia de archivos; no se ejecutó ningún comando de Git.
- El código se copió **sin modificaciones**; no se refactorizó ni se reformateó nada.
