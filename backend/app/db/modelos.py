"""Modelos ORM (SQLAlchemy 2.0) del esquema ResiData.

Mapean 1:1 las tablas creadas por los scripts de ``/database``:
``roles``, ``usuarios``, ``contenedores``, ``categorias_residuo``,
``reglas_servo``, ``historico_clasificaciones``, ``alertas`` y
``configuracion``. Se incluye ademas la vista ``vw_historico_detalle``.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Rol(Base):
    """Catalogo de roles del panel web."""

    __tablename__ = "roles"
    __table_args__ = (
        UniqueConstraint("nombre", name="uq_roles_nombre"),
        CheckConstraint(
            "nombre IN ('administrador', 'operador')",
            name="ck_roles_nombre_valido",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(30), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text)

    usuarios: Mapped[List["Usuario"]] = relationship(back_populates="rol")


class Usuario(Base):
    """Usuario que accede al panel web."""

    __tablename__ = "usuarios"
    __table_args__ = (
        UniqueConstraint("correo", name="uq_usuarios_correo"),
        CheckConstraint(
            r"correo ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$'",
            name="ck_usuarios_correo_formato",
        ),
        CheckConstraint(
            "char_length(btrim(nombre)) > 0",
            name="ck_usuarios_nombre_no_vacio",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    correo: Mapped[str] = mapped_column(String(180), nullable=False)
    contrasena_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("roles.id", name="fk_usuarios_rol", ondelete="RESTRICT")
    )
    activo: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true"), default=True
    )
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), default=func.now()
    )
    ultimo_acceso: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    rol: Mapped["Rol"] = relationship(back_populates="usuarios", lazy="joined")
    alertas_atendidas: Mapped[List["Alerta"]] = relationship(back_populates="usuario_atencion")


class Contenedor(Base):
    """Nodo ESP32-CAM registrado en el sistema."""

    __tablename__ = "contenedores"
    __table_args__ = (
        UniqueConstraint("nombre", name="uq_contenedores_nombre"),
        UniqueConstraint("api_key_hash", name="uq_contenedores_api_key_hash"),
        CheckConstraint(
            "estado IN ('activo', 'inactivo', 'mantenimiento')",
            name="ck_contenedores_estado",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    ubicacion: Mapped[str] = mapped_column(String(200), nullable=False)
    estado: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'activo'"), default="activo"
    )
    api_key_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    ultima_conexion: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), default=func.now()
    )

    clasificaciones: Mapped[List["HistoricoClasificacion"]] = relationship(
        back_populates="contenedor"
    )
    alertas: Mapped[List["Alerta"]] = relationship(back_populates="contenedor")


class CategoriaResiduo(Base):
    """Categoria que la IA puede dictaminar."""

    __tablename__ = "categorias_residuo"
    __table_args__ = (
        UniqueConstraint("nombre", name="uq_categorias_residuo_nombre"),
        CheckConstraint(
            "nivel_peligrosidad BETWEEN 1 AND 3",
            name="ck_categorias_peligrosidad",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50), nullable=False)
    nivel_peligrosidad: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    color_bolsa: Mapped[str] = mapped_column(String(30), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text)

    regla_servo: Mapped[Optional["ReglaServo"]] = relationship(
        back_populates="categoria", uselist=False
    )
    clasificaciones: Mapped[List["HistoricoClasificacion"]] = relationship(
        back_populates="categoria"
    )


class ReglaServo(Base):
    """Angulo del servomotor SG90 por categoria (relacion 1:1)."""

    __tablename__ = "reglas_servo"
    __table_args__ = (
        UniqueConstraint("categoria_id", name="uq_reglas_servo_categoria"),
        CheckConstraint("angulo BETWEEN 0 AND 180", name="ck_reglas_servo_angulo"),
        Index(
            "uq_reglas_servo_por_defecto",
            "es_por_defecto",
            unique=True,
            postgresql_where=text("es_por_defecto"),
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    categoria_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("categorias_residuo.id", name="fk_reglas_servo_categoria", ondelete="CASCADE"),
    )
    angulo: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    es_por_defecto: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false"), default=False
    )

    categoria: Mapped["CategoriaResiduo"] = relationship(back_populates="regla_servo")


class HistoricoClasificacion(Base):
    """Registro de cada clasificacion realizada por la IA."""

    __tablename__ = "historico_clasificaciones"
    __table_args__ = (
        CheckConstraint(
            "confianza >= 0 AND confianza <= 1", name="ck_historico_confianza"
        ),
        CheckConstraint("angulo BETWEEN 0 AND 180", name="ck_historico_angulo"),
        CheckConstraint("tiempo_inferencia_ms >= 0", name="ck_historico_tiempo"),
        CheckConstraint("char_length(btrim(ruta_imagen)) > 0", name="ck_historico_ruta"),
        Index("ix_historico_fecha_hora", text("fecha_hora DESC")),
        Index("ix_historico_contenedor_id", "contenedor_id"),
        Index("ix_historico_categoria_id", "categoria_id"),
        Index("ix_historico_contenedor_fecha", "contenedor_id", text("fecha_hora DESC")),
        Index("ix_historico_categoria_fecha", "categoria_id", text("fecha_hora DESC")),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    fecha_hora: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), default=func.now()
    )
    contenedor_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("contenedores.id", name="fk_historico_contenedor", ondelete="RESTRICT"),
    )
    categoria_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "categorias_residuo.id", name="fk_historico_categoria", ondelete="RESTRICT"
        ),
    )
    confianza: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    angulo: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    ruta_imagen: Mapped[str] = mapped_column(String(500), nullable=False)
    tiempo_inferencia_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    corregida_manualmente: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false"), default=False
    )

    contenedor: Mapped["Contenedor"] = relationship(back_populates="clasificaciones")
    categoria: Mapped["CategoriaResiduo"] = relationship(back_populates="clasificaciones")
    alertas: Mapped[List["Alerta"]] = relationship(back_populates="historico")


class Alerta(Base):
    """Alerta operativa generada por el backend."""

    __tablename__ = "alertas"
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('residuo_peligroso', 'baja_confianza', 'error_contenedor', 'sistema')",
            name="ck_alertas_tipo",
        ),
        CheckConstraint(
            "(atendida = FALSE AND fecha_atencion IS NULL) "
            "OR (atendida = TRUE AND fecha_atencion IS NOT NULL)",
            name="ck_alertas_atencion_coherente",
        ),
        CheckConstraint(
            "atendida_por IS NULL OR atendida = TRUE",
            name="ck_alertas_autor_coherente",
        ),
        Index("ix_alertas_atendida", "atendida"),
        Index("ix_alertas_fecha_creacion", text("fecha_creacion DESC")),
        Index("ix_alertas_atendida_fecha", "atendida", text("fecha_creacion DESC")),
        Index("ix_alertas_contenedor_id", "contenedor_id"),
        Index("ix_alertas_historico_id", "historico_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    historico_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "historico_clasificaciones.id", name="fk_alertas_historico", ondelete="RESTRICT"
        ),
    )
    contenedor_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("contenedores.id", name="fk_alertas_contenedor", ondelete="RESTRICT"),
    )
    tipo: Mapped[str] = mapped_column(String(40), nullable=False)
    mensaje: Mapped[str] = mapped_column(Text, nullable=False)
    atendida: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false"), default=False
    )
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), default=func.now()
    )
    fecha_atencion: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    atendida_por: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("usuarios.id", name="fk_alertas_atendida_por", ondelete="SET NULL")
    )

    historico: Mapped["HistoricoClasificacion"] = relationship(back_populates="alertas")
    contenedor: Mapped["Contenedor"] = relationship(back_populates="alertas")
    usuario_atencion: Mapped[Optional["Usuario"]] = relationship(back_populates="alertas_atendidas")


class Configuracion(Base):
    """Parametro de configuracion clave/valor."""

    __tablename__ = "configuracion"

    clave: Mapped[str] = mapped_column(String(60), primary_key=True)
    valor: Mapped[str] = mapped_column(String(255), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text)


class VistaHistoricoDetalle(Base):
    """Vista de solo lectura ``vw_historico_detalle`` (historico + catalogos)."""

    __tablename__ = "vw_historico_detalle"

    clasificacion_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    fecha_hora: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    confianza: Mapped[Decimal] = mapped_column(Numeric(5, 4))
    angulo: Mapped[int] = mapped_column(SmallInteger)
    ruta_imagen: Mapped[str] = mapped_column(String(500))
    tiempo_inferencia_ms: Mapped[int] = mapped_column(Integer)
    corregida_manualmente: Mapped[bool] = mapped_column(Boolean)
    categoria_id: Mapped[int] = mapped_column(BigInteger)
    categoria_nombre: Mapped[str] = mapped_column(String(50))
    nivel_peligrosidad: Mapped[int] = mapped_column(SmallInteger)
    color_bolsa: Mapped[str] = mapped_column(String(30))
    contenedor_id: Mapped[int] = mapped_column(BigInteger)
    contenedor_nombre: Mapped[str] = mapped_column(String(100))
    contenedor_ubicacion: Mapped[str] = mapped_column(String(200))
