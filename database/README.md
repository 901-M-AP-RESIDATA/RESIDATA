# ResiData - Base de Datos

Scripts SQL de la base de datos **PostgreSQL** del proyecto ResiData (sistema IoT/IA de clasificación de residuos en tiempo real).

## Contenido

| Archivo | Descripción |
| --- | --- |
| `01_esquema.sql` | Tablas, restricciones, claves foráneas y índices. |
| `02_datos_iniciales.sql` | Catálogos, configuración, vista `vw_historico_detalle` y datos de prueba. |
| `03_consultas_dashboard.sql` | Consultas de métricas e históricos para el panel web. |
| `04_rollback.sql` | Elimina la vista y todas las tablas (con sus datos). |

## Requisitos

- PostgreSQL 15 o superior (validado en PostgreSQL 18).
- Cliente `psql` disponible (por defecto en `C:\Program Files\PostgreSQL\<version>\bin`).
- Codificación de la base de datos: UTF8.

## Orden de ejecución

Los scripts son **idempotentes**: pueden ejecutarse varias veces sin romper nada.

1. `01_esquema.sql` (crea la estructura).
2. `02_datos_iniciales.sql` (carga catálogos, vista y datos de prueba).
3. `03_consultas_dashboard.sql` (opcional: solo consulta).
4. `04_rollback.sql` (destructivo: solo si se desea reiniciar).

---

## Ejecución desde PowerShell

### 1. Agregar `psql` al PATH (por sesión)

```powershell
$env:Path += ";C:\Program Files\PostgreSQL\18\bin"
```

### 2. Crear la base de datos `residata`

```powershell
# Solicita la contraseña del usuario postgres
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h 127.0.0.1 -c "CREATE DATABASE residata ENCODING 'UTF8' TEMPLATE template0;"
```

> Si la base ya existe, PostgreSQL devolverá un error; se puede ignorar.

### 3. Ejecutar los scripts

```powershell
$env:PGPASSWORD = "TU_CONTRASENA"

# Fase 1: esquema
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h 127.0.0.1 -d residata -v ON_ERROR_STOP=1 -f ".\database\01_esquema.sql"

# Fase 2: datos iniciales + vista
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h 127.0.0.1 -d residata -v ON_ERROR_STOP=1 -f ".\database\02_datos_iniciales.sql"

# Fase 3: consultas del dashboard
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h 127.0.0.1 -d residata -f ".\database\03_consultas_dashboard.sql"

# Rollback (destructivo)
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h 127.0.0.1 -d residata -v ON_ERROR_STOP=1 -f ".\database\04_rollback.sql"

Remove-Item Env:\PGPASSWORD   # limpiar la variable al terminar
```

> `-v ON_ERROR_STOP=1` detiene la ejecución ante el primer error.
> La opción `-R` evita el empaquetado de resultados ANSI si se redirige a un archivo:
> `... | Out-File -Encoding utf8 salida.txt`.

### 4. Verificar la carga

```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h 127.0.0.1 -d residata -c "SELECT COUNT(*) AS clasificaciones FROM historico_clasificaciones;"
```

---

## Ejecución desde pgAdmin

1. Abrir pgAdmin y conectarse al servidor PostgreSQL local.
2. Clic derecho en **Databases** → **Create** → **Database…** y crear `residata` (Encoding: UTF-8).
3. Clic derecho sobre la base `residata` → **Query Tool**.
4. Abrir cada script con **File → Open** (`01_esquema.sql`, `02_datos_iniciales.sql`, …).
5. Ejecutar con **F5** (o el botón ▶) en el orden indicado.
6. Verificar en el esquema `public` (panel izquierdo) que aparecen tablas y la vista `vw_historico_detalle`.

Para `03_consultas_dashboard.sql`, ejecutar con **F5** y revisar la pestaña **Data Output**.

---

## Modelo de datos

Ver el diagrama entidad-relación en [`../docs/diagrama_er.md`](../docs/diagrama_er.md) y el
[`diccionario de datos`](../docs/diccionario_datos.md).

### Notas de diseño

- **Identificadores**: `GENERATED ALWAYS AS IDENTITY` (sin `SERIAL`), seguro ante escrituras concurrentes.
- **Integridad referencial**: `ON DELETE RESTRICT` en histórico y alertas (no se pierde trazabilidad);
  `ON DELETE CASCADE` de categoría hacia reglas_servo; `ON DELETE SET NULL` en `alertas.atendida_por`.
- **Fechas**: todas en `TIMESTAMPTZ` (con zona horaria) y `DEFAULT now()`.
- **Imágenes**: solo se almacena la **ruta** del archivo (`ruta_imagen`), nunca binarios.
- **Concurrencia**: sin bloqueos innecesarios; se usan índices `DESC` y compuestos para las
  consultas más frecuentes del dashboard.
- **Seguridad**: `contrasena_hash` y `api_key_hash` guardan hashes; el usuario administrador se
  crea desde el backend, nunca con contraseñas en SQL.
