# ResiData - Diagrama Entidad-Relación

Diagrama del modelo relacional de la base de datos PostgreSQL de ResiData.

## Diagrama Mermaid

```mermaid
erDiagram
    roles ||--o{ usuarios : "rol_id"

    usuarios {
        bigint  id PK "GENERATED ALWAYS AS IDENTITY"
        varchar nombre "NOT NULL"
        varchar correo UK "NOT NULL, formato email"
        varchar contrasena_hash "NOT NULL"
        bigint  rol_id FK "NOT NULL -> roles.id"
        boolean activo "NOT NULL DEFAULT TRUE"
        timestamptz fecha_creacion "NOT NULL DEFAULT now()"
        timestamptz ultimo_acceso "NULL"
    }

    roles {
        bigint  id PK "GENERATED ALWAYS AS IDENTITY"
        varchar nombre UK "administrador | operador"
        text    descripcion "NULL"
    }

    contenedores {
        bigint  id PK "GENERATED ALWAYS AS IDENTITY"
        varchar nombre UK "NOT NULL"
        varchar ubicacion "NOT NULL"
        varchar estado "activo | inactivo | mantenimiento"
        varchar api_key_hash UK "NOT NULL"
        timestamptz ultima_conexion "NULL"
        timestamptz fecha_creacion "NOT NULL DEFAULT now()"
    }

    categorias_residuo {
        bigint  id PK "GENERATED ALWAYS AS IDENTITY"
        varchar nombre UK "NOT NULL"
        smallint nivel_peligrosidad "1-3"
        varchar color_bolsa "NOT NULL"
        text    descripcion "NULL"
    }

    reglas_servo {
        bigint  id PK "GENERATED ALWAYS AS IDENTITY"
        bigint  categoria_id FK,UK "NOT NULL -> categorias_residuo.id"
        smallint angulo "0-180"
        boolean es_por_defecto "NOT NULL DEFAULT FALSE"
    }

    historico_clasificaciones {
        bigint  id PK "GENERATED ALWAYS AS IDENTITY"
        timestamptz fecha_hora "NOT NULL DEFAULT now()"
        bigint  contenedor_id FK "NOT NULL -> contenedores.id"
        bigint  categoria_id FK "NOT NULL -> categorias_residuo.id"
        numeric confianza "NUMERIC(5,4) 0-1"
        smallint angulo "0-180"
        varchar ruta_imagen "NOT NULL (solo ruta)"
        integer tiempo_inferencia_ms "NOT NULL >= 0"
        boolean corregida_manualmente "NOT NULL DEFAULT FALSE"
    }

    alertas {
        bigint  id PK "GENERATED ALWAYS AS IDENTITY"
        bigint  historico_id FK "NOT NULL -> historico_clasificaciones.id"
        bigint  contenedor_id FK "NOT NULL -> contenedores.id"
        varchar tipo "residuo_peligroso | baja_confianza | error_contenedor | sistema"
        text    mensaje "NOT NULL"
        boolean atendida "NOT NULL DEFAULT FALSE"
        timestamptz fecha_creacion "NOT NULL DEFAULT now()"
        timestamptz fecha_atencion "NULL"
        bigint  atendida_por FK "NULL -> usuarios.id"
    }

    configuracion {
        varchar clave PK "NOT NULL"
        varchar valor "NOT NULL"
        text    descripcion "NULL"
    }

    categorias_residuo ||--|| reglas_servo                : "categoria_id (1:1)"
    categorias_residuo ||--o{ historico_clasificaciones   : "categoria_id"
    contenedores       ||--o{ historico_clasificaciones   : "contenedor_id"
    historico_clasificaciones ||--o{ alertas             : "historico_id"
    contenedores       ||--o{ alertas                    : "contenedor_id"
    usuarios           |o--o{ alertas                    : "atendida_por"
```

## Relaciones principales

| Relación | Cardinalidad | Regla de borrado |
| --- | --- | --- |
| `roles` → `usuarios` | 1 : N | `RESTRICT` |
| `categorias_residuo` → `reglas_servo` | 1 : 1 | `CASCADE` |
| `categorias_residuo` → `historico_clasificaciones` | 1 : N | `RESTRICT` |
| `contenedores` → `historico_clasificaciones` | 1 : N | `RESTRICT` |
| `historico_clasificaciones` → `alertas` | 1 : N | `RESTRICT` |
| `contenedores` → `alertas` | 1 : N | `RESTRICT` |
| `usuarios` → `alertas` (`atendida_por`) | 1 : N (opcional) | `SET NULL` |

## Notas

- Todas las claves primarias usan `GENERATED ALWAYS AS IDENTITY`.
- Todas las fechas son `TIMESTAMPTZ`.
- `configuracion` es una tabla clave/valor independiente (sin relaciones).
- La vista `vw_historico_detalle` desnormaliza `historico_clasificaciones` + `categorias_residuo` + `contenedores`.
