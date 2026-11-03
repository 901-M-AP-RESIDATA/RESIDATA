-- =====================================================================
--  ResiData - Script 02: Datos iniciales, vista y datos de prueba
--  Motor: PostgreSQL 15+ (validado en PostgreSQL 18)
--  Notas:
--    * Script idempotente (ON CONFLICT / WHERE NOT EXISTS).
--    * NO inserta usuarios ni contrasenas: el admin se crea desde el backend.
--    * Carga ~30 clasificaciones repartidas en varios dias y genera alertas.
-- =====================================================================

SET client_encoding TO 'UTF8';

-- ---------------------------------------------------------------------
-- Roles base
-- ---------------------------------------------------------------------
INSERT INTO roles (nombre, descripcion) VALUES
    ('administrador', 'Acceso total: configuracion, usuarios, reportes y alertas.'),
    ('operador',      'Consulta de metricas, historicos y atencion de alertas.')
ON CONFLICT (nombre) DO NOTHING;

-- ---------------------------------------------------------------------
-- Categorias de residuo
-- ---------------------------------------------------------------------
INSERT INTO categorias_residuo (nombre, nivel_peligrosidad, color_bolsa, descripcion) VALUES
    ('Organico',   1, 'verde', 'Residuos biodegradables: restos de comida, hojas, cascaras.'),
    ('Inorganico', 2, 'azul',  'Residuos reciclables no biodegradables: plastico, vidrio, metal, papel.'),
    ('Peligroso',  3, 'rojo',  'Residuos con riesgo biologico o quimico: pilas, baterias, residuos sanitarios.')
ON CONFLICT (nombre) DO NOTHING;

-- ---------------------------------------------------------------------
-- Reglas del servomotor SG90 por categoria (relacion 1:1)
--   Organico -> 0,  Inorganico -> 90,  Peligroso -> 180 (por defecto)
-- ---------------------------------------------------------------------
INSERT INTO reglas_servo (categoria_id, angulo, es_por_defecto)
SELECT c.id, v.angulo, v.es_por_defecto
FROM (VALUES
        ('Organico',   0::SMALLINT,  FALSE),
        ('Inorganico', 90::SMALLINT, FALSE),
        ('Peligroso',  180::SMALLINT, TRUE)
     ) AS v(nombre, angulo, es_por_defecto)
JOIN categorias_residuo c ON c.nombre = v.nombre
ON CONFLICT (categoria_id) DO NOTHING;

-- ---------------------------------------------------------------------
-- Contenedores (nodos ESP32-CAM de ejemplo)
-- En produccion el api_key_hash se genera en el backend.
-- ---------------------------------------------------------------------
INSERT INTO contenedores (nombre, ubicacion, estado, api_key_hash, ultima_conexion) VALUES
    ('Contenedor Patio A',   'Edificio A - Patio central', 'activo',
     '$argon2id$v=19$m=65536,t=3,p=4$seed-hash-contenedor-patio-a', now() - interval '5 minutes'),
    ('Contenedor Entrada B', 'Edificio B - Acceso principal', 'activo',
     '$argon2id$v=19$m=65536,t=3,p=4$seed-hash-contenedor-entrada-b', now() - interval '2 hours')
ON CONFLICT (nombre) DO NOTHING;

-- ---------------------------------------------------------------------
-- Configuracion de negocio
-- ---------------------------------------------------------------------
INSERT INTO configuracion (clave, valor, descripcion) VALUES
    ('umbral_confianza',           '0.60', 'Confianza minima (0-1) para aceptar la clasificacion de la IA.'),
    ('categoria_baja_confianza',   'Peligroso', 'Categoria asignada cuando la confianza no supera el umbral.'),
    ('tiempo_max_inferencia_ms',   '2000', 'Tiempo maximo aceptable de inferencia en milisegundos.'),
    ('retencion_historico_dias',   '90',   'Dias de retencion del historico de clasificaciones.')
ON CONFLICT (clave) DO NOTHING;

-- ---------------------------------------------------------------------
-- Datos de prueba: ~30 clasificaciones repartidas en varios dias.
-- Solo se insertan si el historico esta vacio (idempotente).
-- El angulo se toma de reglas_servo para mantener coherencia.
-- ---------------------------------------------------------------------
WITH generadas AS (
    SELECT
        g,
        (ARRAY['Organico', 'Inorganico', 'Peligroso'])[1 + ((g - 1) % 3)]        AS categoria_nombre,
        (ARRAY['Contenedor Patio A', 'Contenedor Entrada B'])[1 + ((g - 1) % 2)] AS contenedor_nombre,
        now() - ((g % 15) || ' days')::interval
              - ((g * 37 % 20) || ' hours')::interval                             AS fecha_hora,
        round((0.55 + random() * 0.44)::numeric, 4)                              AS confianza,
        (250 + floor(random() * 1500))::int                                     AS tiempo_ms,
        (random() < 0.12)                                                       AS corregida
    FROM generate_series(1, 30) AS gs(g)
)
INSERT INTO historico_clasificaciones (
    fecha_hora, contenedor_id, categoria_id, confianza, angulo,
    ruta_imagen, tiempo_inferencia_ms, corregida_manualmente
)
SELECT
    gen.fecha_hora,
    con.id,
    cat.id,
    gen.confianza,
    reg.angulo,
    'imagenes/clasificaciones/' || to_char(gen.fecha_hora, 'YYYY-MM-DD')
        || '/clasif_' || lpad(gen.g::text, 4, '0') || '.jpg',
    gen.tiempo_ms,
    gen.corregida
FROM generadas gen
JOIN contenedores        con ON con.nombre = gen.contenedor_nombre
JOIN categorias_residuo  cat ON cat.nombre = gen.categoria_nombre
JOIN reglas_servo        reg ON reg.categoria_id = cat.id
WHERE NOT EXISTS (SELECT 1 FROM historico_clasificaciones);

-- ---------------------------------------------------------------------
-- Alertas de prueba: residuos peligrosos -> alerta inmediata.
-- ---------------------------------------------------------------------
INSERT INTO alertas (historico_id, contenedor_id, tipo, mensaje, fecha_creacion)
SELECT
    h.id,
    h.contenedor_id,
    'residuo_peligroso',
    'Residuo peligroso detectado (confianza ' || h.confianza || '). Requiere atencion inmediata.',
    h.fecha_hora
FROM historico_clasificaciones h
JOIN categorias_residuo c ON c.id = h.categoria_id
WHERE c.nombre = 'Peligroso'
  AND NOT EXISTS (SELECT 1 FROM alertas WHERE tipo = 'residuo_peligroso');

-- ---------------------------------------------------------------------
-- Alertas de prueba: clasificaciones por debajo del umbral de confianza.
-- ---------------------------------------------------------------------
INSERT INTO alertas (historico_id, contenedor_id, tipo, mensaje, fecha_creacion)
SELECT
    h.id,
    h.contenedor_id,
    'baja_confianza',
    'Clasificacion con baja confianza (' || h.confianza || '). Revisar manualmente.',
    h.fecha_hora
FROM historico_clasificaciones h
WHERE h.confianza < (SELECT valor::numeric FROM configuracion WHERE clave = 'umbral_confianza')
  AND NOT EXISTS (SELECT 1 FROM alertas WHERE tipo = 'baja_confianza');

-- ---------------------------------------------------------------------
-- Vista: vw_historico_detalle
-- Une historico + categoria + contenedor para el panel web.
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_historico_detalle AS
SELECT
    h.id                          AS clasificacion_id,
    h.fecha_hora,
    h.confianza,
    h.angulo,
    h.ruta_imagen,
    h.tiempo_inferencia_ms,
    h.corregida_manualmente,
    c.id                          AS categoria_id,
    c.nombre                      AS categoria_nombre,
    c.nivel_peligrosidad,
    c.color_bolsa,
    con.id                        AS contenedor_id,
    con.nombre                    AS contenedor_nombre,
    con.ubicacion                 AS contenedor_ubicacion
FROM historico_clasificaciones h
JOIN categorias_residuo c ON c.id = h.categoria_id
JOIN contenedores       con ON con.id = h.contenedor_id;

COMMENT ON VIEW vw_historico_detalle IS 'Vista desnormalizada de clasificaciones con categoria y contenedor.';

-- =====================================================================
-- Fin del script 02_datos_iniciales.sql
-- =====================================================================
