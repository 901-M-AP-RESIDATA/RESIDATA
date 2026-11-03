# HU-09 — Notificación de Residuos Peligrosos

- **ID:** HU-09
- **Nombre:** Notificación de Residuos Peligrosos
- **Responsable:** Juan Carlos
- **Prioridad:** Media
- **Carpeta:** `HU-09_Notificacion-Peligrosos`
- **Origen:** `RESIDATA completo` (copia íntegra, sin modificar el código)

## Tareas técnicas cubiertas

| Tarea técnica | Archivo(s) | Detalle |
| --- | --- | --- |
| Payload de alerta para detecciones "Peligroso" | `backend/app/schemas/alerta.py`, `backend/app/api/v1/alertas.py` | `AlertaLeer` (id, histórico, contenedor, tipo, mensaje, `atendida`, fechas, autor, nombres) y `AlertaActualizar`; tipos `residuo_peligroso`, `baja_confianza`, `error_contenedor`, `sistema` |
| Componente de alerta flotante (Toast/Snackbar) | `frontend/src/lib/components/Toast.svelte`, `frontend/src/lib/stores/toast.svelte.ts` | Contenedor fijo arriba a la derecha (`z-[60]`), `role="alert"`, cierre manual y autocierre; store con `exito`/`error`/`info`/`peligro` |
| Estilos destacados (borde/fondo rojo, icono de peligro, alerta sonora opcional) | `frontend/src/app.css`, `frontend/src/lib/components/Toast.svelte`, `frontend/src/lib/util/sonido.ts` | Paleta `--color-peligro-500/600/700` reservada a alertas; variante `peligro` con `border-peligro-500 bg-peligro-600 text-white` e icono de triángulo; `aria-live="assertive"`; aviso sonoro de dos tonos (880/660 Hz) con Web Audio API, activable/desactivable |
| Almacenamiento del estado de alertas pendientes en el panel de administración | `frontend/src/lib/stores/alertas.svelte.ts`, `frontend/src/routes/(panel)/alertas/+page.svelte`, `frontend/src/lib/api/alertas.ts` | Store `alertas.pendientes` cargado con `GET /alertas?atendida=false&limite=50`; se actualiza al recibir `alerta_peligroso` por WebSocket; página con vistas Pendientes/Atendidas/Todas, filtro por tipo y acción "atender" (`PATCH /alertas/{id}`) |

### Flujo implementado

```
procesamiento.py (categoría nivel >= 3)
        └─ crea Alerta(tipo="residuo_peligroso")
        └─ gestor.difundir({"tipo": "alerta_peligroso", "data": AlertaLeer})

WebSocket ──► stores/tiempoReal.ts ──► stores/alertas.svelte.ts
                                          ├─ pendientes = [alerta, ...]
                                          ├─ toasts.peligro("Residuo peligroso", mensaje)
                                          └─ reproducirAlerta()  (si sonidoActivo)
```

### Avisos

- **El toast de peligro no se autocierra:** `toasts.peligro()` usa `duracion = 0`; permanece hasta que
  el usuario lo cierre. Es intencional para alertas críticas.
- **La alerta sonora requiere interacción previa del usuario:** los navegadores bloquean `AudioContext`
  hasta el primer gesto; el código lo crea de forma perezosa y falla en silencio.
- **El rojo es exclusivo de esta HU:** `app.css` documenta que la paleta `peligro-*` se reserva solo
  para alertas de residuos peligrosos.

## Archivos copiados

| Archivo | Tipo | Origen |
| --- | --- | --- |
| `backend/app/api/v1/alertas.py` | HU-09 | `RESIDATA completo/backend/app/api/v1/alertas.py` |
| `backend/app/schemas/alerta.py` | HU-09 (compartido con HU-05) | `RESIDATA completo/backend/app/schemas/alerta.py` |
| `frontend/src/lib/stores/alertas.svelte.ts` | HU-09 | `RESIDATA completo/frontend/src/lib/stores/alertas.svelte.ts` |
| `frontend/src/lib/stores/toast.svelte.ts` | HU-09 (compartido con HU-08/10) | `RESIDATA completo/frontend/src/lib/stores/toast.svelte.ts` |
| `frontend/src/lib/components/Toast.svelte` | HU-09 | `RESIDATA completo/frontend/src/lib/components/Toast.svelte` |
| `frontend/src/routes/(panel)/alertas/+page.svelte` | HU-09 | `RESIDATA completo/frontend/src/routes/(panel)/alertas/+page.svelte` |
| `frontend/src/lib/api/alertas.ts` | HU-09 | `RESIDATA completo/frontend/src/lib/api/alertas.ts` |
| `frontend/src/lib/util/sonido.ts` | HU-09 | `RESIDATA completo/frontend/src/lib/util/sonido.ts` |
| `frontend/src/app.css` | Base (compartido con HU-08/10) | `RESIDATA completo/frontend/src/app.css` |

**Total: 9 archivos**, todos verificados byte a byte contra el origen.

## Dependencias de otras HU

| HU | Qué se reutiliza |
| --- | --- |
| **HU-03** | `backend/app/core/deps.py` (`SesionBd`, `UsuarioActual`), `core/excepciones.py` (`ErrorNoEncontrado`), `schemas/comun.py` (`RespuestaPaginada`, `construir_paginada`) |
| **HU-05** | `services/procesamiento.py` crea la alerta `residuo_peligroso` y la difunde |
| **HU-07** | `db/modelos.py` (`Alerta`, `HistoricoClasificacion`, `Contenedor`, `CategoriaResiduo`) |
| **HU-08** | `stores/tiempoReal.ts`, `lib/config.ts` (`SONIDO_ALERTAS`), `lib/tipos/index.ts` (`Alerta`, `EventoWS`, `FiltrosAlertas`), `lib/api/cliente.ts`, `lib/util/formato.ts`, y los componentes `Boton`, `Cargando`, `EstadoVacio`, `Insignia`, `Tarjeta`; también `routes/+layout.svelte` (monta `<Toast/>`) y `(panel)/+layout.svelte` |
| **HU-10** | `lib/api/index.ts` re-exporta `alertas`; esta HU no depende de HU-10, pero el barrel de HU-08 sí |

- **Consecuencia:** esta carpeta **no compila/arranca aislada**; necesita la base del frontend de HU-08
  y el backend de HU-03/05/07. Se documenta como dependencia, sin modificar código.

## Credenciales

- **No se copió ningún `.env` ni configuración con secretos.**
- Esta entrega no contiene contraseñas, API keys ni tokens.

## Notas

- **Archivos compartidos:** `schemas/alerta.py` (con HU-05), `stores/toast.svelte.ts` y `app.css`
  (con HU-08/10) se copian completos aquí (regla 7).
- **`app.css` es la Base del tema Tailwind v4** que el frontend de HU-08 necesitaba para compilar; queda
  resuelta con esta entrega.
- **Paginación:** el backend usa `limite=20` por defecto (máx. 1000); el store y la página piden 50.
- **Sin Git:** esta entrega se creó solo con copia de archivos; no se ejecutó ningún comando de Git.
- El código se copió **sin modificaciones**; no se refactorizó ni se reformateó nada.
