-- =====================================================================
--  ResiData - Script 03: Consultas para el dashboard
--  Motor: PostgreSQL 15+ (validado en PostgreSQL 18)
--  Notas:
--    * Solo lectura (SELECT). Ejecutable cuantas veces se quiera.
--    * Pensado para ejecutarse con psql -f (usa \echo como separadores).
-- =====================================================================

SET client_encoding TO 'UTF8';

-- =====================================================================
-- 1) Residuos por categoria
-- =====================================================================
\echo '=== 1) Residuos por categoria ==='
SELECT
    c.nombre                                   AS categoria,
    c.nivel_peligrosidad,
    COUNT(h.id)                                AS total,
    ROUND(100.0 * COUNT(h.id) / NULLIF(SUM(COUNT(h.id)) OVER (), 0), 2) AS porcentaje
FROM categorias_residuo c
LEFT JOIN historico_clasificaciones h ON h.categoria_id = c.id
GROUP BY c.id, c.nombre, c.nivel_peligrosidad
ORDER BY total DESC;

-- =====================================================================
-- 2) Residuos por dia (ultimos 30 dias)
-- =====================================================================
\echo '=== 2) Residuos por dia (ultimos 30 dias) ==='
SELECT
    d.dia::date          AS dia,
    COUNT(h.id)          AS total,
    COUNT(*) FILTER (WHERE c.nombre = 'Organico')   AS organicos,
    COUNT(*) FILTER (WHERE c.nombre = 'Inorganico') AS inorganicos,
    COUNT(*) FILTER (WHERE c.nombre = 'Peligroso')  AS peligrosos
FROM generate_series(
        (CURRENT_DATE - INTERVAL '29 days')::date,
        CURRENT_DATE,
        INTERVAL '1 day'
     ) AS d(dia)
LEFT JOIN historico_clasificaciones h
       ON h.fecha_hora >= d.dia AND h.fecha_hora < d.dia + INTERVAL '1 day'
LEFT JOIN categorias_residuo c ON c.id = h.categoria_id
GROUP BY d.dia
ORDER BY d.dia DESC;

-- =====================================================================
-- 3) Residuos por contenedor
-- =====================================================================
\echo '=== 3) Residuos por contenedor ==='
SELECT
    con.nombre                     AS contenedor,
    con.ubicacion,
    con.estado,
    COUNT(h.id)                    AS total,
    MAX(h.fecha_hora)              AS ultima_clasificacion
FROM contenedores con
LEFT JOIN historico_clasificaciones h ON h.contenedor_id = con.id
GROUP BY con.id, con.nombre, con.ubicacion, con.estado
ORDER BY total DESC;

-- =====================================================================
-- 4) Confianza promedio por categoria
-- =====================================================================
\echo '=== 4) Confianza promedio por categoria ==='
SELECT
    c.nombre                        AS categoria,
    COUNT(h.id)                     AS total,
    ROUND(AVG(h.confianza), 4)      AS confianza_promedio,
    ROUND(MIN(h.confianza), 4)      AS confianza_minima,
    ROUND(MAX(h.confianza), 4)      AS confianza_maxima
FROM categorias_residuo c
LEFT JOIN historico_clasificaciones h ON h.categoria_id = c.id
GROUP BY c.id, c.nombre
ORDER BY confianza_promedio DESC NULLS LAST;

-- =====================================================================
-- 5) Clasificaciones con baja confianza (por debajo del umbral)
-- =====================================================================
\echo '=== 5) Clasificaciones con baja confianza ==='
SELECT
    h.id                AS clasificacion_id,
    h.fecha_hora,
    c.nombre            AS categoria,
    h.confianza,
    con.nombre          AS contenedor,
    h.corregida_manualmente
FROM historico_clasificaciones h
JOIN categorias_residuo c  ON c.id = h.categoria_id
JOIN contenedores       con ON con.id = h.contenedor_id
WHERE h.confianza < (SELECT valor::numeric FROM configuracion WHERE clave = 'umbral_confianza')
ORDER BY h.confianza ASC, h.fecha_hora DESC;

-- =====================================================================
-- 6) Alertas pendientes (no atendidas)
-- =====================================================================
\echo '=== 6) Alertas pendientes ==='
SELECT
    a.id            AS alerta_id,
    a.fecha_creacion,
    a.tipo,
    a.mensaje,
    con.nombre      AS contenedor,
    c.nombre        AS categoria
FROM alertas a
JOIN contenedores       con ON con.id = a.contenedor_id
JOIN historico_clasificaciones h ON h.id = a.historico_id
JOIN categorias_residuo c  ON c.id = h.categoria_id
WHERE a.atendida = FALSE
ORDER BY a.fecha_creacion DESC;

-- =====================================================================
-- 7) Ultimas 20 lecturas
-- =====================================================================
\echo '=== 7) Ultimas 20 lecturas ==='
SELECT
    clasificacion_id,
    fecha_hora,
    categoria_nombre,
    contenedor_nombre,
    confianza,
    angulo,
    tiempo_inferencia_ms,
    corregida_manualmente
FROM vw_historico_detalle
ORDER BY fecha_hora DESC
LIMIT 20;

-- =====================================================================
-- Fin del script 03_consultas_dashboard.sql
-- =====================================================================
