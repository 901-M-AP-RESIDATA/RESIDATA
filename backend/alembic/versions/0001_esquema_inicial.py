"""Esquema inicial ResiData

Crea todas las tablas, restricciones, indices y la vista
``vw_historico_detalle``. Equivale a ``/database/01_esquema.sql``.

Revision ID: 0001_esquema_inicial
Revises:
Create Date: 2026-10-10

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_esquema_inicial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_VISTA_HISTORICO = """
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
JOIN contenedores       con ON con.id = h.contenedor_id
"""


def upgrade() -> None:
    # --- roles --------------------------------------------------------
    op.create_table(
        "roles",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("nombre", sa.String(length=30), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.UniqueConstraint("nombre", name="uq_roles_nombre"),
        sa.CheckConstraint(
            "nombre IN ('administrador', 'operador')", name="ck_roles_nombre_valido"
        ),
    )

    # --- usuarios -----------------------------------------------------
    op.create_table(
        "usuarios",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("nombre", sa.String(length=120), nullable=False),
        sa.Column("correo", sa.String(length=180), nullable=False),
        sa.Column("contrasena_hash", sa.String(length=255), nullable=False),
        sa.Column("rol_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "activo", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.Column(
            "fecha_creacion",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("ultimo_acceso", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("correo", name="uq_usuarios_correo"),
        sa.CheckConstraint(
            r"correo ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$'", name="ck_usuarios_correo_formato"
        ),
        sa.CheckConstraint(
            "char_length(btrim(nombre)) > 0", name="ck_usuarios_nombre_no_vacio"
        ),
        sa.ForeignKeyConstraint(
            ["rol_id"], ["roles.id"], name="fk_usuarios_rol", ondelete="RESTRICT"
        ),
    )

    # --- contenedores -------------------------------------------------
    op.create_table(
        "contenedores",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("ubicacion", sa.String(length=200), nullable=False),
        sa.Column(
            "estado", sa.String(length=20), nullable=False, server_default=sa.text("'activo'")
        ),
        sa.Column("api_key_hash", sa.String(length=255), nullable=False),
        sa.Column("ultima_conexion", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "fecha_creacion",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("nombre", name="uq_contenedores_nombre"),
        sa.UniqueConstraint("api_key_hash", name="uq_contenedores_api_key_hash"),
        sa.CheckConstraint(
            "estado IN ('activo', 'inactivo', 'mantenimiento')", name="ck_contenedores_estado"
        ),
    )

    # --- categorias_residuo -------------------------------------------
    op.create_table(
        "categorias_residuo",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("nombre", sa.String(length=50), nullable=False),
        sa.Column("nivel_peligrosidad", sa.SmallInteger(), nullable=False),
        sa.Column("color_bolsa", sa.String(length=30), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.UniqueConstraint("nombre", name="uq_categorias_residuo_nombre"),
        sa.CheckConstraint(
            "nivel_peligrosidad BETWEEN 1 AND 3", name="ck_categorias_peligrosidad"
        ),
    )

    # --- reglas_servo -------------------------------------------------
    op.create_table(
        "reglas_servo",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("categoria_id", sa.BigInteger(), nullable=False),
        sa.Column("angulo", sa.SmallInteger(), nullable=False),
        sa.Column(
            "es_por_defecto", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.UniqueConstraint("categoria_id", name="uq_reglas_servo_categoria"),
        sa.CheckConstraint("angulo BETWEEN 0 AND 180", name="ck_reglas_servo_angulo"),
        sa.ForeignKeyConstraint(
            ["categoria_id"],
            ["categorias_residuo.id"],
            name="fk_reglas_servo_categoria",
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "uq_reglas_servo_por_defecto",
        "reglas_servo",
        ["es_por_defecto"],
        unique=True,
        postgresql_where=sa.text("es_por_defecto"),
    )

    # --- historico_clasificaciones ------------------------------------
    op.create_table(
        "historico_clasificaciones",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column(
            "fecha_hora",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("contenedor_id", sa.BigInteger(), nullable=False),
        sa.Column("categoria_id", sa.BigInteger(), nullable=False),
        sa.Column("confianza", sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column("angulo", sa.SmallInteger(), nullable=False),
        sa.Column("ruta_imagen", sa.String(length=500), nullable=False),
        sa.Column("tiempo_inferencia_ms", sa.Integer(), nullable=False),
        sa.Column(
            "corregida_manualmente",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.CheckConstraint(
            "confianza >= 0 AND confianza <= 1", name="ck_historico_confianza"
        ),
        sa.CheckConstraint("angulo BETWEEN 0 AND 180", name="ck_historico_angulo"),
        sa.CheckConstraint("tiempo_inferencia_ms >= 0", name="ck_historico_tiempo"),
        sa.CheckConstraint("char_length(btrim(ruta_imagen)) > 0", name="ck_historico_ruta"),
        sa.ForeignKeyConstraint(
            ["contenedor_id"],
            ["contenedores.id"],
            name="fk_historico_contenedor",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["categoria_id"],
            ["categorias_residuo.id"],
            name="fk_historico_categoria",
            ondelete="RESTRICT",
        ),
    )
    op.create_index(
        "ix_historico_fecha_hora",
        "historico_clasificaciones",
        [sa.text("fecha_hora DESC")],
    )
    op.create_index(
        "ix_historico_contenedor_id", "historico_clasificaciones", ["contenedor_id"]
    )
    op.create_index(
        "ix_historico_categoria_id", "historico_clasificaciones", ["categoria_id"]
    )
    op.create_index(
        "ix_historico_contenedor_fecha",
        "historico_clasificaciones",
        ["contenedor_id", sa.text("fecha_hora DESC")],
    )
    op.create_index(
        "ix_historico_categoria_fecha",
        "historico_clasificaciones",
        ["categoria_id", sa.text("fecha_hora DESC")],
    )

    # --- alertas ------------------------------------------------------
    op.create_table(
        "alertas",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("historico_id", sa.BigInteger(), nullable=False),
        sa.Column("contenedor_id", sa.BigInteger(), nullable=False),
        sa.Column("tipo", sa.String(length=40), nullable=False),
        sa.Column("mensaje", sa.Text(), nullable=False),
        sa.Column(
            "atendida", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.Column(
            "fecha_creacion",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("fecha_atencion", sa.DateTime(timezone=True), nullable=True),
        sa.Column("atendida_por", sa.BigInteger(), nullable=True),
        sa.CheckConstraint(
            "tipo IN ('residuo_peligroso', 'baja_confianza', 'error_contenedor', 'sistema')",
            name="ck_alertas_tipo",
        ),
        sa.CheckConstraint(
            "(atendida = FALSE AND fecha_atencion IS NULL) "
            "OR (atendida = TRUE AND fecha_atencion IS NOT NULL)",
            name="ck_alertas_atencion_coherente",
        ),
        sa.CheckConstraint(
            "atendida_por IS NULL OR atendida = TRUE", name="ck_alertas_autor_coherente"
        ),
        sa.ForeignKeyConstraint(
            ["historico_id"],
            ["historico_clasificaciones.id"],
            name="fk_alertas_historico",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["contenedor_id"],
            ["contenedores.id"],
            name="fk_alertas_contenedor",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["atendida_por"],
            ["usuarios.id"],
            name="fk_alertas_atendida_por",
            ondelete="SET NULL",
        ),
    )
    op.create_index("ix_alertas_atendida", "alertas", ["atendida"])
    op.create_index("ix_alertas_fecha_creacion", "alertas", [sa.text("fecha_creacion DESC")])
    op.create_index(
        "ix_alertas_atendida_fecha",
        "alertas",
        ["atendida", sa.text("fecha_creacion DESC")],
    )
    op.create_index("ix_alertas_contenedor_id", "alertas", ["contenedor_id"])
    op.create_index("ix_alertas_historico_id", "alertas", ["historico_id"])

    # --- configuracion ------------------------------------------------
    op.create_table(
        "configuracion",
        sa.Column("clave", sa.String(length=60), primary_key=True),
        sa.Column("valor", sa.String(length=255), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
    )

    # --- vista --------------------------------------------------------
    op.execute(_VISTA_HISTORICO)


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS vw_historico_detalle")
    op.drop_table("configuracion")
    op.drop_index("ix_alertas_historico_id", table_name="alertas")
    op.drop_index("ix_alertas_contenedor_id", table_name="alertas")
    op.drop_index("ix_alertas_atendida_fecha", table_name="alertas")
    op.drop_index("ix_alertas_fecha_creacion", table_name="alertas")
    op.drop_index("ix_alertas_atendida", table_name="alertas")
    op.drop_table("alertas")
    op.drop_index("ix_historico_categoria_fecha", table_name="historico_clasificaciones")
    op.drop_index("ix_historico_contenedor_fecha", table_name="historico_clasificaciones")
    op.drop_index("ix_historico_categoria_id", table_name="historico_clasificaciones")
    op.drop_index("ix_historico_contenedor_id", table_name="historico_clasificaciones")
    op.drop_index("ix_historico_fecha_hora", table_name="historico_clasificaciones")
    op.drop_table("historico_clasificaciones")
    op.drop_index("uq_reglas_servo_por_defecto", table_name="reglas_servo")
    op.drop_table("reglas_servo")
    op.drop_table("categorias_residuo")
    op.drop_table("contenedores")
    op.drop_table("usuarios")
    op.drop_table("roles")
