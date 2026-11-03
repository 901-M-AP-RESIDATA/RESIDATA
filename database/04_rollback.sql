-- =====================================================================
--  ResiData - Script 04: Rollback (eliminacion de objetos)
--  Motor: PostgreSQL 15+ (validado en PostgreSQL 18)
--  ADVERTENCIA: elimina TODAS las tablas, la vista y sus datos.
--  El orden respeta las dependencias (hijas antes que padres).
-- =====================================================================

SET client_encoding TO 'UTF8';

DROP VIEW  IF EXISTS vw_historico_detalle;

DROP TABLE IF EXISTS alertas                     CASCADE;
DROP TABLE IF EXISTS historico_clasificaciones   CASCADE;
DROP TABLE IF EXISTS reglas_servo                CASCADE;
DROP TABLE IF EXISTS contenedores                CASCADE;
DROP TABLE IF EXISTS usuarios                    CASCADE;
DROP TABLE IF EXISTS categorias_residuo          CASCADE;
DROP TABLE IF EXISTS roles                       CASCADE;
DROP TABLE IF EXISTS configuracion               CASCADE;

-- =====================================================================
-- Fin del script 04_rollback.sql
-- =====================================================================
