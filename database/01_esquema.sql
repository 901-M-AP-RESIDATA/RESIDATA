-- =====================================================================
--  ResiData - Sistema IoT/IA de clasificacion de residuos
--  Script 01: Esquema, restricciones e indices
--  Motor: PostgreSQL 15+ (validado en PostgreSQL 18)
--  Autor: Equipo ResiData - ITIC-901
--  Notas:
--    * Script idempotente: puede ejecutarse varias veces sin romper nada.
--    * Nomenclatura en snake_case, contenido en espanol.
--    * Todas las fechas usan TIMESTAMPTZ (UTC-aware).
--    * Solo se guarda la RUTA de la imagen, nunca binarios.
-- =====================================================================

SET client_encoding TO 'UTF8';

-- ---------------------------------------------------------------------
-- Tabla: roles
-- Catalogo de roles del sistema (administrador, operador).
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS roles (
    id            BIGINT       GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre        VARCHAR(30)  NOT NULL,
    descripcion   TEXT,
    CONSTRAINT uq_roles_nombre       UNIQUE (nombre),
    CONSTRAINT ck_roles_nombre_valido CHECK (nombre IN ('administrador', 'operador'))
);

COMMENT ON TABLE  roles             IS 'Catalogo de roles del panel web.';
COMMENT ON COLUMN roles.nombre      IS 'Nombre del rol: administrador u operador.';
COMMENT ON COLUMN roles.descripcion IS 'Descripcion de los permisos del rol.';

-- ---------------------------------------------------------------------
-- Tabla: usuarios
-- Usuarios del panel web. La contrasena se almacena SIEMPRE hasheada.
-- El usuario administrador inicial se crea desde el backend (no en SQL).
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuarios (
    id                BIGINT       GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre            VARCHAR(120) NOT NULL,
    correo            VARCHAR(180) NOT NULL,
    contrasena_hash   VARCHAR(255) NOT NULL,
    rol_id            BIGINT       NOT NULL,
    activo            BOOLEAN      NOT NULL DEFAULT TRUE,
    fecha_creacion    TIMESTAMPTZ  NOT NULL DEFAULT now(),
    ultimo_acceso     TIMESTAMPTZ,
    CONSTRAINT uq_usuarios_correo       UNIQUE (correo),
    CONSTRAINT ck_usuarios_correo_formato CHECK (correo ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$'),
    CONSTRAINT ck_usuarios_nombre_no_vacio CHECK (char_length(btrim(nombre)) > 0),
    CONSTRAINT fk_usuarios_rol FOREIGN KEY (rol_id)
        REFERENCES roles (id) ON UPDATE CASCADE ON DELETE RESTRICT
);

COMMENT ON TABLE  usuarios                  IS 'Usuarios que acceden al panel web.';
COMMENT ON COLUMN usuarios.contrasena_hash  IS 'Hash de la contrasena (bcrypt/argon2). Nunca texto plano.';
COMMENT ON COLUMN usuarios.rol_id           IS 'Rol asignado (administrador u operador).';
COMMENT ON COLUMN usuarios.activo           IS 'Indica si el usuario puede iniciar sesion.';
COMMENT ON COLUMN usuarios.ultimo_acceso    IS 'Fecha/hora del ultimo inicio de sesion exitoso.';

-- ---------------------------------------------------------------------
-- Tabla: contenedores
-- Nodos ESP32-CAM registrados. api_key_hash autentica cada nodo.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS contenedores (
    id                BIGINT       GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre            VARCHAR(100) NOT NULL,
    ubicacion         VARCHAR(200) NOT NULL,
    estado            VARCHAR(20)  NOT NULL DEFAULT 'activo',
    api_key_hash      VARCHAR(255) NOT NULL,
    ultima_conexion   TIMESTAMPTZ,
    fecha_creacion    TIMESTAMPTZ  NOT NULL DEFAULT now(),
    CONSTRAINT uq_contenedores_nombre        UNIQUE (nombre),
    CONSTRAINT uq_contenedores_api_key_hash  UNIQUE (api_key_hash),
    CONSTRAINT ck_contenedores_estado        CHECK (estado IN ('activo', 'inactivo', 'mantenimiento'))
);

COMMENT ON TABLE  contenedores                 IS 'Nodos ESP32-CAM registrados en el sistema.';
COMMENT ON COLUMN contenedores.ubicacion       IS 'Descripcion fisica de la ubicacion del contenedor.';
COMMENT ON COLUMN contenedores.estado          IS 'Estado operativo: activo, inactivo o mantenimiento.';
COMMENT ON COLUMN contenedores.api_key_hash    IS 'Hash del API key del nodo. Nunca se guarda la clave en claro.';
COMMENT ON COLUMN contenedores.ultima_conexion IS 'Ultima vez que el nodo se comunico con el backend.';

-- ---------------------------------------------------------------------
-- Tabla: categorias_residuo
-- Catalogo de categorias que la IA puede dictaminar.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS categorias_residuo (
    id                   BIGINT       GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre               VARCHAR(50)  NOT NULL,
    nivel_peligrosidad   SMALLINT     NOT NULL,
    color_bolsa          VARCHAR(30)  NOT NULL,
    descripcion          TEXT,
    CONSTRAINT uq_categorias_residuo_nombre UNIQUE (nombre),
    CONSTRAINT ck_categorias_peligrosidad   CHECK (nivel_peligrosidad BETWEEN 1 AND 3)
);

COMMENT ON TABLE  categorias_residuo                      IS 'Categorias de clasificacion de residuos.';
COMMENT ON COLUMN categorias_residuo.nivel_peligrosidad   IS 'Nivel de peligrosidad: 1 (bajo), 2 (medio), 3 (alto).';
COMMENT ON COLUMN categorias_residuo.color_bolsa          IS 'Color de bolsa asociado a la categoria.';

-- ---------------------------------------------------------------------
-- Tabla: reglas_servo
-- Angulo del servomotor SG90 asociado a cada categoria (1:1).
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reglas_servo (
    id               BIGINT    GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    categoria_id     BIGINT    NOT NULL,
    angulo           SMALLINT  NOT NULL,
    es_por_defecto   BOOLEAN   NOT NULL DEFAULT FALSE,
    CONSTRAINT uq_reglas_servo_categoria UNIQUE (categoria_id),
    CONSTRAINT ck_reglas_servo_angulo    CHECK (angulo BETWEEN 0 AND 180),
    CONSTRAINT fk_reglas_servo_categoria FOREIGN KEY (categoria_id)
        REFERENCES categorias_residuo (id) ON UPDATE CASCADE ON DELETE CASCADE
);

COMMENT ON TABLE  reglas_servo                IS 'Angulo del servo SG90 por categoria (relacion 1:1).';
COMMENT ON COLUMN reglas_servo.angulo         IS 'Angulo de giro en grados (0-180).';
COMMENT ON COLUMN reglas_servo.es_por_defecto IS 'Marca la regla usada cuando la categoria no se resuelve.';

-- Solo puede existir una regla marcada como por defecto.
CREATE UNIQUE INDEX IF NOT EXISTS uq_reglas_servo_por_defecto
    ON reglas_servo (es_por_defecto)
    WHERE es_por_defecto;

-- ---------------------------------------------------------------------
-- Tabla: historico_clasificaciones
-- Registro de cada clasificacion realizada por la IA. Tabla de alto
-- volumen: disenada para escrituras concurrentes desde varios nodos.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS historico_clasificaciones (
    id                      BIGINT        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fecha_hora              TIMESTAMPTZ   NOT NULL DEFAULT now(),
    contenedor_id           BIGINT        NOT NULL,
    categoria_id            BIGINT        NOT NULL,
    confianza               NUMERIC(5,4)  NOT NULL,
    angulo                  SMALLINT      NOT NULL,
    ruta_imagen             VARCHAR(500)  NOT NULL,
    tiempo_inferencia_ms    INTEGER       NOT NULL,
    corregida_manualmente   BOOLEAN       NOT NULL DEFAULT FALSE,
    CONSTRAINT ck_historico_confianza  CHECK (confianza >= 0 AND confianza <= 1),
    CONSTRAINT ck_historico_angulo     CHECK (angulo BETWEEN 0 AND 180),
    CONSTRAINT ck_historico_tiempo     CHECK (tiempo_inferencia_ms >= 0),
    CONSTRAINT ck_historico_ruta       CHECK (char_length(btrim(ruta_imagen)) > 0),
    CONSTRAINT fk_historico_contenedor FOREIGN KEY (contenedor_id)
        REFERENCES contenedores (id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_historico_categoria  FOREIGN KEY (categoria_id)
        REFERENCES categorias_residuo (id) ON UPDATE CASCADE ON DELETE RESTRICT
);

COMMENT ON TABLE  historico_clasificaciones                         IS 'Historico de cada clasificacion realizada por la IA.';
COMMENT ON COLUMN historico_clasificaciones.fecha_hora              IS 'Momento de la clasificacion (TIMESTAMPTZ).';
COMMENT ON COLUMN historico_clasificaciones.confianza               IS 'Confianza de la inferencia entre 0 y 1 (NUMERIC(5,4)).';
COMMENT ON COLUMN historico_clasificaciones.angulo                  IS 'Angulo aplicado al servo (0-180).';
COMMENT ON COLUMN historico_clasificaciones.ruta_imagen             IS 'Ruta relativa del archivo de imagen. Nunca binarios.';
COMMENT ON COLUMN historico_clasificaciones.tiempo_inferencia_ms    IS 'Duracion de la inferencia en milisegundos.';
COMMENT ON COLUMN historico_clasificaciones.corregida_manualmente   IS 'TRUE si un operador corrigio la categoria asignada.';

-- Indices para el panel de metricas e historicos.
CREATE INDEX IF NOT EXISTS ix_historico_fecha_hora
    ON historico_clasificaciones (fecha_hora DESC);
CREATE INDEX IF NOT EXISTS ix_historico_contenedor_id
    ON historico_clasificaciones (contenedor_id);
CREATE INDEX IF NOT EXISTS ix_historico_categoria_id
    ON historico_clasificaciones (categoria_id);
CREATE INDEX IF NOT EXISTS ix_historico_contenedor_fecha
    ON historico_clasificaciones (contenedor_id, fecha_hora DESC);
CREATE INDEX IF NOT EXISTS ix_historico_categoria_fecha
    ON historico_clasificaciones (categoria_id, fecha_hora DESC);

-- ---------------------------------------------------------------------
-- Tabla: alertas
-- Alertas generadas por el backend (residuos peligrosos, baja
-- confianza, fallos de nodo, etc.).
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS alertas (
    id              BIGINT       GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    historico_id    BIGINT       NOT NULL,
    contenedor_id   BIGINT       NOT NULL,
    tipo            VARCHAR(40)  NOT NULL,
    mensaje         TEXT         NOT NULL,
    atendida        BOOLEAN      NOT NULL DEFAULT FALSE,
    fecha_creacion  TIMESTAMPTZ  NOT NULL DEFAULT now(),
    fecha_atencion  TIMESTAMPTZ,
    atendida_por    BIGINT,
    CONSTRAINT ck_alertas_tipo CHECK (
        tipo IN ('residuo_peligroso', 'baja_confianza', 'error_contenedor', 'sistema')
    ),
    CONSTRAINT ck_alertas_atencion_coherente CHECK (
        (atendida = FALSE AND fecha_atencion IS NULL)
        OR (atendida = TRUE AND fecha_atencion IS NOT NULL)
    ),
    CONSTRAINT ck_alertas_autor_coherente CHECK (
        atendida_por IS NULL OR atendida = TRUE
    ),
    CONSTRAINT fk_alertas_historico FOREIGN KEY (historico_id)
        REFERENCES historico_clasificaciones (id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_alertas_contenedor FOREIGN KEY (contenedor_id)
        REFERENCES contenedores (id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_alertas_atendida_por FOREIGN KEY (atendida_por)
        REFERENCES usuarios (id) ON UPDATE CASCADE ON DELETE SET NULL
);

COMMENT ON TABLE  alertas                 IS 'Alertas operativas generadas por el backend.';
COMMENT ON COLUMN alertas.tipo            IS 'Tipo: residuo_peligroso, baja_confianza, error_contenedor, sistema.';
COMMENT ON COLUMN alertas.atendida        IS 'TRUE cuando un operador/admin atendio la alerta.';
COMMENT ON COLUMN alertas.fecha_atencion  IS 'Fecha/hora en que se atendio la alerta.';
COMMENT ON COLUMN alertas.atendida_por    IS 'Usuario que atendio la alerta (NULL si el sistema lo hizo).';

-- Indices para el panel de alertas (pendientes y por fecha).
CREATE INDEX IF NOT EXISTS ix_alertas_atendida
    ON alertas (atendida);
CREATE INDEX IF NOT EXISTS ix_alertas_fecha_creacion
    ON alertas (fecha_creacion DESC);
CREATE INDEX IF NOT EXISTS ix_alertas_atendida_fecha
    ON alertas (atendida, fecha_creacion DESC);
CREATE INDEX IF NOT EXISTS ix_alertas_contenedor_id
    ON alertas (contenedor_id);
CREATE INDEX IF NOT EXISTS ix_alertas_historico_id
    ON alertas (historico_id);

-- ---------------------------------------------------------------------
-- Tabla: configuracion
-- Parametros de negocio clave/valor editables sin recompilar.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS configuracion (
    clave        VARCHAR(60)  PRIMARY KEY,
    valor        VARCHAR(255) NOT NULL,
    descripcion  TEXT
);

COMMENT ON TABLE  configuracion             IS 'Parametros de configuracion del sistema (clave/valor).';
COMMENT ON COLUMN configuracion.clave       IS 'Identificador unico del parametro.';
COMMENT ON COLUMN configuracion.valor       IS 'Valor serializado del parametro.';

-- =====================================================================
-- Fin del script 01_esquema.sql
-- =====================================================================
