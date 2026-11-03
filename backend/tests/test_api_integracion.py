"""Pruebas de integracion del API ResiData (requieren base de datos).

Cubren el flujo completo: autenticacion, catalogos, CRUD de usuarios y
contenedores, ingesta IoT con clasificacion simulada, historico, alertas y
dashboard.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.core.config import obtener_configuracion
from app.db.modelos import Alerta, Contenedor, HistoricoClasificacion, Usuario
from app.db.sesion import sesion_ambito
from app.main import app

# Bytes minimos que simulan una imagen JPEG (el modo simulado no la decodifica).
IMAGEN_FALSA = b"\xff\xd8\xff\xe0" + b"\x00" * 64


@pytest.fixture(scope="module")
def cliente():
    with TestClient(app) as cliente_test:
        yield cliente_test


@pytest.fixture(scope="module")
def cabeceras(cliente: TestClient) -> dict[str, str]:
    config = obtener_configuracion()
    respuesta = cliente.post(
        "/api/v1/auth/login",
        data={"username": config.admin_correo, "password": config.admin_contrasena},
    )
    assert respuesta.status_code == 200, respuesta.text
    token = respuesta.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health(cliente: TestClient) -> None:
    respuesta = cliente.get("/api/v1/health")
    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] in {"ok", "degradado"}


def test_login_credenciales_invalidas(cliente: TestClient) -> None:
    respuesta = cliente.post(
        "/api/v1/auth/login",
        data={"username": "nadie@residata.local", "password": "malo"},
    )
    assert respuesta.status_code == 401


def test_perfil_requiere_token(cliente: TestClient) -> None:
    assert cliente.get("/api/v1/auth/me").status_code == 401


def test_perfil(cliente: TestClient, cabeceras: dict[str, str]) -> None:
    respuesta = cliente.get("/api/v1/auth/me", headers=cabeceras)
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["correo"] == obtener_configuracion().admin_correo
    assert "contrasena" not in cuerpo
    assert cuerpo["rol"]["nombre"] == "administrador"


def test_refresco_token(cliente: TestClient) -> None:
    config = obtener_configuracion()
    login = cliente.post(
        "/api/v1/auth/login",
        data={"username": config.admin_correo, "password": config.admin_contrasena},
    ).json()
    respuesta = cliente.post(
        "/api/v1/auth/refresh", json={"refresh_token": login["refresh_token"]}
    )
    assert respuesta.status_code == 200
    assert "access_token" in respuesta.json()


def test_catalogos(cliente: TestClient, cabeceras: dict[str, str]) -> None:
    roles = cliente.get("/api/v1/roles", headers=cabeceras)
    assert roles.status_code == 200
    assert {rol["nombre"] for rol in roles.json()} >= {"administrador", "operador"}

    categorias = cliente.get("/api/v1/categorias", headers=cabeceras)
    assert categorias.status_code == 200
    assert len(categorias.json()) == 3


def test_crud_usuario(cliente: TestClient, cabeceras: dict[str, str]) -> None:
    sufijo = uuid.uuid4().hex[:8]
    correo = f"prueba_{sufijo}@residata.local"
    crear = cliente.post(
        "/api/v1/usuarios",
        headers=cabeceras,
        json={"nombre": "Usuario Prueba", "correo": correo, "contrasena": "secreta123", "rol_id": 2},
    )
    assert crear.status_code == 201, crear.text
    usuario_id = crear.json()["id"]

    try:
        assert cliente.get(f"/api/v1/usuarios/{usuario_id}", headers=cabeceras).status_code == 200

        repetido = cliente.post(
            "/api/v1/usuarios",
            headers=cabeceras,
            json={
                "nombre": "Otro",
                "correo": correo,
                "contrasena": "secreta123",
                "rol_id": 2,
            },
        )
        assert repetido.status_code == 409

        actualizar = cliente.patch(
            f"/api/v1/usuarios/{usuario_id}",
            headers=cabeceras,
            json={"nombre": "Usuario Renombrado"},
        )
        assert actualizar.status_code == 200
        assert actualizar.json()["nombre"] == "Usuario Renombrado"
    finally:
        assert cliente.delete(f"/api/v1/usuarios/{usuario_id}", headers=cabeceras).status_code == 204


def test_crud_contenedor(cliente: TestClient, cabeceras: dict[str, str]) -> None:
    sufijo = uuid.uuid4().hex[:8]
    crear = cliente.post(
        "/api/v1/contenedores",
        headers=cabeceras,
        json={"nombre": f"Contenedor Prueba {sufijo}", "ubicacion": "Laboratorio"},
    )
    assert crear.status_code == 201, crear.text
    contenedor = crear.json()
    assert contenedor["api_key"]
    contenedor_id = contenedor["id"]

    try:
        detalle = cliente.get(f"/api/v1/contenedores/{contenedor_id}", headers=cabeceras)
        assert detalle.status_code == 200
        assert detalle.json()["total_clasificaciones"] == 0

        regenerar = cliente.post(
            f"/api/v1/contenedores/{contenedor_id}/regenerar-clave", headers=cabeceras
        )
        assert regenerar.status_code == 200
        assert regenerar.json()["api_key"] != contenedor["api_key"]
    finally:
        assert (
            cliente.delete(f"/api/v1/contenedores/{contenedor_id}", headers=cabeceras).status_code
            == 204
        )


def test_ingesta_iot(cliente: TestClient, cabeceras: dict[str, str]) -> None:
    sufijo = uuid.uuid4().hex[:8]
    contenedor = cliente.post(
        "/api/v1/contenedores",
        headers=cabeceras,
        json={"nombre": f"Contenedor IoT {sufijo}", "ubicacion": "Patio"},
    ).json()
    contenedor_id = contenedor["id"]
    api_key = contenedor["api_key"]

    respuesta = cliente.post(
        "/api/v1/dispositivo/clasificar",
        headers={"X-Api-Key": api_key},
        files={"imagen": ("captura.jpg", IMAGEN_FALSA, "image/jpeg")},
    )
    assert respuesta.status_code == 200, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["angulo"] in {0, 90, 180}
    assert 0.0 <= cuerpo["confianza"] <= 1.0
    historico_id = cuerpo["historico"]["id"]

    # Sin API key valida debe rechazar.
    sin_clave = cliente.post(
        "/api/v1/dispositivo/clasificar",
        files={"imagen": ("captura.jpg", IMAGEN_FALSA, "image/jpeg")},
    )
    assert sin_clave.status_code == 401

    historico = cliente.get(
        "/api/v1/historico",
        headers=cabeceras,
        params={"contenedor_id": contenedor_id},
    )
    assert historico.status_code == 200
    assert historico.json()["total"] >= 1

    # Limpieza: alertas -> historico -> contenedor.
    with sesion_ambito() as db:
        db.execute(delete(Alerta).where(Alerta.historico_id == historico_id))
        db.execute(
            delete(HistoricoClasificacion).where(
                HistoricoClasificacion.contenedor_id == contenedor_id
            )
        )
        db.execute(delete(Contenedor).where(Contenedor.id == contenedor_id))


def test_dashboard(cliente: TestClient, cabeceras: dict[str, str]) -> None:
    respuesta = cliente.get("/api/v1/dashboard/resumen", headers=cabeceras)
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert set(cuerpo) == {
        "total_hoy",
        "total_historico",
        "por_categoria",
        "por_dia",
        "confianza_promedio",
        "alertas_pendientes",
        "ultimas",
    }
    assert len(cuerpo["por_dia"]) == 7


def test_flujo_alertas(cliente: TestClient, cabeceras: dict[str, str]) -> None:
    pendientes = cliente.get(
        "/api/v1/alertas", headers=cabeceras, params={"atendida": "false", "limite": 1}
    )
    assert pendientes.status_code == 200
    items = pendientes.json()["items"]
    if not items:
        pytest.skip("No hay alertas pendientes en la base de datos.")

    alerta_id = items[0]["id"]
    atender = cliente.patch(
        f"/api/v1/alertas/{alerta_id}", headers=cabeceras, json={"atendida": True}
    )
    assert atender.status_code == 200
    assert atender.json()["atendida"] is True
    assert atender.json()["fecha_atencion"] is not None

    # Reabrir para no alterar el estado inicial.
    cliente.patch(f"/api/v1/alertas/{alerta_id}", headers=cabeceras, json={"atendida": False})
