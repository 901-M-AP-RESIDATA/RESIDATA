# ResiData - Diccionario de Datos

Descripción detallada de todas las tablas, columnas, tipos y restricciones de la
base de datos PostgreSQL de ResiData.

**Convenciones**

- `PK` = llave primaria · `FK` = llave foránea · `UK` = valor único.
- Tipos: `BIGINT`, `SMALLINT`, `INTEGER`, `NUMERIC`, `VARCHAR`, `TEXT`, `BOOLEAN`, `TIMESTAMPTZ`.
- Todas las fechas son `TIMESTAMPTZ` (con zona horaria).

---

## 1. `roles`

Catálogo de roles del panel web.

| Campo | Tipo | Restricciones | Descripción |
| --- | --- | --- | --- |
| `id` | BIGINT | PK, GENERATED ALWAYS AS IDENTITY | Identificador del rol. |
| `nombre` | VARCHAR(30) | NOT NULL, UK, CHECK `nombre IN ('administrador','operador')` | Nombre del rol. |
| `descripcion` | TEXT | NULL | Descripción de los permisos del rol. |

---

## 2. `usuarios`

Usuarios que acceden al panel web. La contraseña se almacena siempre hasheada.
El usuario administrador inicial se crea desde el backend.

| Campo | Tipo | Restricciones | Descripción |
| --- | --- | --- | --- |
| `id` | BIGINT | PK, GENERATED ALWAYS AS IDENTITY | Identificador del usuario. |
| `nombre` | VARCHAR(120) | NOT NULL, CHECK no vacío | Nombre completo del usuario. |
| `correo` | VARCHAR(180) | NOT NULL, UK, CHECK formato email | Correo de inicio de sesión. |
| `contrasena_hash` | VARCHAR(255) | NOT NULL | Hash de la contraseña (bcrypt/argon2). Nunca texto plano. |
| `rol_id` | BIGINT | NOT NULL, FK → `roles.id` (RESTRICT) | Rol asignado al usuario. |
| `activo` | BOOLEAN | NOT NULL, DEFAULT TRUE | Indica si puede iniciar sesión. |
| `fecha_creacion` | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Fecha de alta. |
| `ultimo_acceso` | TIMESTAMPTZ | NULL | Último inicio de sesión exitoso. |

---

## 3. `contenedores`

Nodos ESP32-CAM registrados en el sistema.

| Campo | Tipo | Restricciones | Descripción |
| --- | --- | --- | --- |
| `id` | BIGINT | PK, GENERATED ALWAYS AS IDENTITY | Identificador del contenedor. |
| `nombre` | VARCHAR(100) | NOT NULL, UK | Nombre del contenedor/nodo. |
| `ubicacion` | VARCHAR(200) | NOT NULL | Ubicación física. |
| `estado` | VARCHAR(20) | NOT NULL, DEFAULT 'activo', CHECK `IN ('activo','inactivo','mantenimiento')` | Estado operativo. |
| `api_key_hash` | VARCHAR(255) | NOT NULL, UK | Hash del API key del nodo. Nunca la clave en claro. |
| `ultima_conexion` | TIMESTAMPTZ | NULL | Última comunicación con el backend. |
| `fecha_creacion` | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Fecha de registro. |

---

## 4. `categorias_residuo`

Categorías que la IA puede dictaminar.

| Campo | Tipo | Restricciones | Descripción |
| --- | --- | --- | --- |
| `id` | BIGINT | PK, GENERATED ALWAYS AS IDENTITY | Identificador de la categoría. |
| `nombre` | VARCHAR(50) | NOT NULL, UK | Nombre (Orgánico, Inorgánico, Peligroso). |
| `nivel_peligrosidad` | SMALLINT | NOT NULL, CHECK `BETWEEN 1 AND 3` | 1 bajo, 2 medio, 3 alto. |
| `color_bolsa` | VARCHAR(30) | NOT NULL | Color de bolsa asociado. |
| `descripcion` | TEXT | NULL | Descripción de la categoría. |

---

## 5. `reglas_servo`

Ángulo del servomotor SG90 por categoría (relación 1:1).

| Campo | Tipo | Restricciones | Descripción |
| --- | --- | --- | --- |
| `id` | BIGINT | PK, GENERATED ALWAYS AS IDENTITY | Identificador de la regla. |
| `categoria_id` | BIGINT | NOT NULL, UK, FK → `categorias_residuo.id` (CASCADE) | Categoría asociada (una regla por categoría). |
| `angulo` | SMALLINT | NOT NULL, CHECK `BETWEEN 0 AND 180` | Ángulo de giro en grados. |
| `es_por_defecto` | BOOLEAN | NOT NULL, DEFAULT FALSE, único parcial cuando es TRUE | Regla usada como respaldo. |

> Índice único parcial `uq_reglas_servo_por_defecto` garantiza que solo una fila tenga `es_por_defecto = TRUE`.

---

## 6. `historico_clasificaciones`

Registro de cada clasificación realizada por la IA. Tabla de alto volumen.

| Campo | Tipo | Restricciones | Descripción |
| --- | --- | --- | --- |
| `id` | BIGINT | PK, GENERATED ALWAYS AS IDENTITY | Identificador de la clasificación. |
| `fecha_hora` | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Momento de la clasificación. |
| `contenedor_id` | BIGINT | NOT NULL, FK → `contenedores.id` (RESTRICT) | Nodo que originó la lectura. |
| `categoria_id` | BIGINT | NOT NULL, FK → `categorias_residuo.id` (RESTRICT) | Categoría dictaminada. |
| `confianza` | NUMERIC(5,4) | NOT NULL, CHECK `BETWEEN 0 AND 1` | Confianza de la inferencia. |
| `angulo` | SMALLINT | NOT NULL, CHECK `BETWEEN 0 AND 180` | Ángulo aplicado al servo. |
| `ruta_imagen` | VARCHAR(500) | NOT NULL, CHECK no vacío | Ruta del archivo de imagen (nunca binarios). |
| `tiempo_inferencia_ms` | INTEGER | NOT NULL, CHECK `>= 0` | Duración de la inferencia en ms. |
| `corregida_manualmente` | BOOLEAN | NOT NULL, DEFAULT FALSE | TRUE si un operador corrigió la categoría. |

**Índices:** `fecha_hora DESC`, `contenedor_id`, `categoria_id`, `(contenedor_id, fecha_hora DESC)`, `(categoria_id, fecha_hora DESC)`.

---

## 7. `alertas`

Alertas operativas generadas por el backend.

| Campo | Tipo | Restricciones | Descripción |
| --- | --- | --- | --- |
| `id` | BIGINT | PK, GENERATED ALWAYS AS IDENTITY | Identificador de la alerta. |
| `historico_id` | BIGINT | NOT NULL, FK → `historico_clasificaciones.id` (RESTRICT) | Clasificación que originó la alerta. |
| `contenedor_id` | BIGINT | NOT NULL, FK → `contenedores.id` (RESTRICT) | Contenedor involucrado. |
| `tipo` | VARCHAR(40) | NOT NULL, CHECK `IN ('residuo_peligroso','baja_confianza','error_contenedor','sistema')` | Tipo de alerta. |
| `mensaje` | TEXT | NOT NULL | Mensaje descriptivo. |
| `atendida` | BOOLEAN | NOT NULL, DEFAULT FALSE | TRUE si ya fue atendida. |
| `fecha_creacion` | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Fecha de generación. |
| `fecha_atencion` | TIMESTAMPTZ | NULL, CHECK coherente con `atendida` | Fecha/hora de atención. |
| `atendida_por` | BIGINT | NULL, FK → `usuarios.id` (SET NULL), CHECK coherente con `atendida` | Usuario que atendió la alerta. |

**Índices:** `atendida`, `fecha_creacion DESC`, `(atendida, fecha_creacion DESC)`, `contenedor_id`, `historico_id`.

**Restricciones de coherencia:**

- `ck_alertas_atencion_coherente`: si `atendida = FALSE` entonces `fecha_atencion IS NULL`; si `atendida = TRUE` entonces `fecha_atencion IS NOT NULL`.
- `ck_alertas_autor_coherente`: `atendida_por` solo puede tener valor si `atendida = TRUE`.

---

## 8. `configuracion`

Parámetros de negocio clave/valor.

| Campo | Tipo | Restricciones | Descripción |
| --- | --- | --- | --- |
| `clave` | VARCHAR(60) | PK, NOT NULL | Identificador del parámetro. |
| `valor` | VARCHAR(255) | NOT NULL | Valor serializado. |
| `descripcion` | TEXT | NULL | Descripción del parámetro. |

**Valores iniciales:** `umbral_confianza = 0.60`, `categoria_baja_confianza = Peligroso`, `tiempo_max_inferencia_ms = 2000`, `retencion_historico_dias = 90`.

---

## Vista `vw_historico_detalle`

Vista de solo lectura que une `historico_clasificaciones` + `categorias_residuo` + `contenedores`.

| Columna | Origen |
| --- | --- |
| `clasificacion_id` | `historico_clasificaciones.id` |
| `fecha_hora` | `historico_clasificaciones.fecha_hora` |
| `confianza` | `historico_clasificaciones.confianza` |
| `angulo` | `historico_clasificaciones.angulo` |
| `ruta_imagen` | `historico_clasificaciones.ruta_imagen` |
| `tiempo_inferencia_ms` | `historico_clasificaciones.tiempo_inferencia_ms` |
| `corregida_manualmente` | `historico_clasificaciones.corregida_manualmente` |
| `categoria_id` | `categorias_residuo.id` |
| `categoria_nombre` | `categorias_residuo.nombre` |
| `nivel_peligrosidad` | `categorias_residuo.nivel_peligrosidad` |
| `color_bolsa` | `categorias_residuo.color_bolsa` |
| `contenedor_id` | `contenedores.id` |
| `contenedor_nombre` | `contenedores.nombre` |
| `contenedor_ubicacion` | `contenedores.ubicacion` |
