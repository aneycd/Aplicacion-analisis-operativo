# tests/test_integracion_api_informe.py
# Pruebas de integración para el endpoint /api/informe.
# Valida que el endpoint responde con la estructura esperada y que los datos
# son consistentes, después de autenticación.

import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import json
import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        # Helper: hacer login como administrador para las rutas protegidas
        def login():
            return client.post("/login", data={
                "usuario": "admin",
                "clave": "Cambiar2026"
            })
        client.login = login
        yield client


def test_api_informe_devuelve_json_valido(client):
    """El endpoint /api/informe debe devolver un JSON válido con las 5 reglas de negocio."""
    client.login()
    respuesta = client.get("/api/informe")
    assert respuesta.status_code == 200, "El endpoint debe responder 200"
    assert respuesta.is_json, "La respuesta debe ser JSON"

    datos = respuesta.get_json()
    assert isinstance(datos, dict), "El JSON debe ser un diccionario"

    claves_esperadas = {
        "r1_metricas_canal",
        "r2_correos_buzon",
        "r3_matriz_asesor_buzon",
        "r4_whatsapp_subcanal",
        "r5_desempeno_asesor",
    }
    claves_obtenidas = set(datos.keys())
    faltantes = claves_esperadas - claves_obtenidas
    assert not faltantes, f"Faltan claves en la respuesta JSON: {faltantes}"


def test_api_informe_estructura_r1(client):
    """La clave r1_metricas_canal debe tener 'canales' y 'resumen'."""
    client.login()
    datos = client.get("/api/informe").get_json()
    r1 = datos["r1_metricas_canal"]

    assert "canales" in r1
    assert "resumen" in r1
    assert isinstance(r1["canales"], list)
    assert len(r1["canales"]) == 4  # 4 canales


def test_api_informe_estructura_r2(client):
    """La clave r2_correos_buzon debe tener 'buzones' y 'resumen'."""
    client.login()
    datos = client.get("/api/informe").get_json()
    r2 = datos["r2_correos_buzon"]

    assert "buzones" in r2
    assert "resumen" in r2
    assert isinstance(r2["buzones"], list)
    assert len(r2["buzones"]) == 6  # 6 buzones del contexto


def test_api_informe_estructura_r5(client):
    """La clave r5_desempeno_asesor debe tener 'asesores' y 'resumen'."""
    client.login()
    datos = client.get("/api/informe").get_json()
    r5 = datos["r5_desempeno_asesor"]

    assert "asesores" in r5
    assert "resumen" in r5
    assert isinstance(r5["asesores"], list)
