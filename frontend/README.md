# ResiData — Frontend (panel de control)

Aplicación web (SPA) del panel de administración de **ResiData**. Consume la API
REST y los eventos WebSocket del backend FastAPI.

## Stack

- **Svelte 5** (runes) + **SvelteKit 3** en modo SPA (cliente)
- **Vite 8** + **TypeScript**
- **Tailwind CSS 4** (configuración CSS-first con `@theme`)
- **Chart.js** y **flatpickr** (se usan en fases posteriores)

## Requisitos

- Node.js 20+ (probado con Node 24)
- El backend corriendo en `http://localhost:8000` (o usar el modo mock)

## Puesta en marcha

```bash
npm install
cp .env.example .env    # ajustar si hace falta
npm run dev             # http://localhost:5173
```

Scripts disponibles:

| Script | Descripción |
| ------ | ----------- |
| `npm run dev` | Servidor de desarrollo |
| `npm run build` | Build de producción (salida en `build/`) |
| `npm run preview` | Sirve el build de producción |
| `npm run check` | Chequeo de tipos de Svelte/TS |

En Windows PowerShell usar `npm.cmd` si la política de ejecución bloquea `npm.ps1`.

## Variables de entorno

Solo las variables con prefijo `VITE_` llegan al navegador (ver `.env.example`):

| Variable | Descripción |
| -------- | ----------- |
| `VITE_API_URL` | URL base del backend (sin barra final) |
| `VITE_USAR_MOCK` | `true` usa datos simulados sin backend |
| `VITE_SONIDO_ALERTAS` | `true` reproduce sonido en alertas de peligro |

En modo mock: `admin@residata.local` / `admin123` (administrador) y
`operador@residata.local` / `operador123` (operador).

## Estructura

```
src/
  app.css                 Tema (Tailwind v4 @theme): paleta blanca + verde
  app.html                Documento base
  lib/
    config.ts             Lectura de variables de entorno
    tipos/index.ts        Tipos del dominio (contrato del API)
    api/                  Cliente HTTP, auth, almacenamiento, mocks
    stores/               Estado con runes (sesion, toast, conexion)
    components/           UI reutilizable (Boton, Modal, Navbar, ...)
  routes/
    +layout.ts/.svelte    Layout raíz (ssr=false) + contenedor de toasts
    +page.ts              Redirige a /dashboard
    +error.svelte         Página de error
    login/                Inicio de sesión (OAuth2 form)
    (panel)/              Grupo protegido: guard de sesión + shell
      +layout.svelte      Sidebar + Navbar + guard
      dashboard/          Métricas en tiempo real
      contenedores/       Gestión de contenedores
      historico/          Histórico con filtros
      alertas/            Centro de alertas
      usuarios/           Gestión de usuarios (solo admin)
```

## Import alias

SvelteKit 3 eliminó `$lib` en favor de `#lib` (subpath imports de Node,
declarados en `package.json`). Los imports usan extensión explícita, p. ej.
`#lib/config.ts` o `#lib/components/Boton.svelte`.

## Convenciones de UI

- Paleta **blanca + verde** (`marca`). El **rojo** (`peligro`) se reserva
  **exclusivamente** para alertas de residuos peligrosos.
- Todos los textos de interfaz en **español**.
- Accesibilidad: `aria-*`, foco visible y soporte de `prefers-reduced-motion`.

## Estado por fases

- [x] **Fase 1** — Scaffolding, tema, cliente API, stores, login, layout y guard.
- [x] **Fase 2** — Dashboard (métricas, gráficas Chart.js y WebSocket en vivo).
- [x] **Fase 3** — Alertas en tiempo real y sonido.
- [x] **Fase 4** — Histórico con filtros y exportación CSV.
- [x] **Fase 5** — Contenedores y usuarios (CRUD).
