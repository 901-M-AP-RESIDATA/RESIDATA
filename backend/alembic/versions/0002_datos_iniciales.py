"""Datos iniciales ResiData

Carga roles, categorias, reglas de servo y configuracion de negocio.
No inserta usuarios (el administrador se crea con ``scripts/crear_admin.py``)
ni datos de prueba de historico (esos son opcionales, ver /database/02).

Revision ID: 0002_datos_iniciales
Revises: 0001_esquema_inicial
Create Date: 2026-10-10

"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = "0002_datos_iniciales"
down_revision: Union[str, None] = "0001_esquema_inicial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO roles (nombre, descripcion) VALUES
            ('administrador', 'Acceso total: configuracion, usuarios, reportes y alertas.'),
            ('operador',      'Consulta de metricas, historicos y atencion de alertas.')
        ON CONFLICT (nombre) DO NOTHING
        """
    )
    op.execute(
        """
        INSERT INTO categorias_residuo (nombre, nivel_peligrosidad, color_bolsa, descripcion) VALUES
            ('Organico',   1, 'verde', 'Residuos biodegradables: restos de comida, hojas, cascaras.'),
            ('Inorganico', 2, 'azul',  'Residuos reciclables no biodegradables: plastico, vidrio, metal, papel.'),
            ('Peligroso',  3, 'rojo',  'Residuos con riesgo biologico o quimico: pilas, baterias, residuos sanitarios.')
        ON CONFLICT (nombre) DO NOTHING
        """
    )
    op.execute(
        """
        INSERT INTO reglas_servo (categoria_id, angulo, es_por_defecto)
        SELECT c.id, v.angulo, v.es_por_defecto
        FROM (VALUES
                ('Organico',   0,   FALSE),
                ('Inorganico', 90,  FALSE),
                ('Peligroso',  180, TRUE)
             ) AS v(nombre, angulo, es_por_defecto)
        JOIN categorias_residuo c ON c.nombre = v.nombre
        ON CONFLICT (categoria_id) DO NOTHING
        """
    )
    op.execute(
        """
        INSERT INTO configuracion (clave, valor, descripcion) VALUES
            ('umbral_confianza',         '0.60', 'Confianza minima (0-1) para aceptar la clasificacion de la IA.'),
            ('categoria_baja_confianza', 'Peligroso', 'Categoria asignada cuando la confianza no supera el umbral.'),
            ('tiempo_max_inferencia_ms', '2000', 'Tiempo maximo aceptable de inferencia en milisegundos.'),
            ('retencion_historico_dias', '90',   'Dias de retencion del historico de clasificaciones.')
        ON CONFLICT (clave) DO NOTHING
        """
    )


def downgrade() -> None:
    op.execute("DELETE FROM configuracion")
    op.execute("DELETE FROM reglas_servo")
    op.execute("DELETE FROM categorias_residuo")
    op.execute("DELETE FROM roles")
