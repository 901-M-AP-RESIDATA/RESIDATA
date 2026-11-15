#!/bin/sh
set -e

echo "==> Verificando esquema de base de datos con Alembic..."
# Intentar upgrade; si las tablas ya existen por los scripts de base de datos, estampar a head
if ! alembic upgrade head 2>&1; then
    echo "==> Tablas existentes detectadas. Estampando versión de Alembic a head..."
    alembic stamp head
fi

echo "==> Creando usuario administrador inicial..."
python scripts/crear_admin.py || true

echo "==> Iniciando FastAPI con Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
