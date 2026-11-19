"""
Pruebas de validación de la app de análisis operativo Contact Center.
Valida que los endpoints respondan y que las reglas de negocio devuelvan
datos consistentes con los insumos (sin inventar valores).
"""

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


def test_app_crea_correctamente():
    """La app Flask debe crearse sin errores."""
    app = create_app()
    assert app is not None


def test_endpoint_health(client):
    """El endpoint /api/health debe responder OK (público, no requiere login)."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["status"] == "ok"


def test_endpoint_insumos(client):
    """El endpoint /api/insumos debe devolver los 3 archivos Excel."""
    client.login()
    resp = client.get("/api/insumos")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["status"] == "ok"
    assert len(data["insumos"]) == 3
    nombres = [a["archivo"] for a in data["insumos"]]
    assert "Control CHATBOT.xlsx" in nombres
    assert "Control llamadas y correos.xlsx" in nombres
    assert "Control WhatsApp.xlsx" in nombres


def test_regla_r1_chatbot_tiene_datos(client):
    """R1 debe devolver datos reales para Chatbot/CORI (no DATO FALTANTE)."""
    client.login()
    resp = client.get("/api/regla-r1")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["regla"] == "R1"
    canales = {c["canal"]: c for c in data["datos"]}
    assert "Chatbot/CORI" in canales
    cb = canales["Chatbot/CORI"]
    assert cb["cantidad_atendida"] != "DATO FALTANTE"
    assert cb["aht"] != "DATO FALTANTE"
    assert isinstance(cb["cantidad_atendida"], int)
    assert cb["cantidad_atendida"] > 0


def test_regla_r2_buzones_dato_faltante(client):
    """R2 debe reportar DATO FALTANTE para buzones no encontrados (regla R6)."""
    client.login()
    resp = client.get("/api/regla-r2")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["regla"] == "R2"
    assert len(data["datos"]["buzones"]) == 6
    buzones = {b["buzon"]: b for b in data["datos"]["buzones"]}
    for nombre in ["Bienes adquiridos", "Centro Asistencia N1", "Centro Asistencia N2",
                   "Operativa CAC PCI", "Servicio oficina virtual", "Soporte CAC"]:
        assert nombre in buzones
        # Como no se confirmó columna de buzón, deben ser DATO FALTANTE
        assert buzones[nombre]["cantidad"] == "DATO FALTANTE"


def test_regla_r3_matriz_vacia_sin_inventar(client):
    """R3 debe reportar matriz vacía sin inventar valores (regla R6)."""
    client.login()
    resp = client.get("/api/regla-r3")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["regla"] == "R3"
    assert data["datos"]["matriz"] == {}
    assert data["datos"]["datos_disponibles"] is False
    assert len(data["datos"]["buzones_sin_columna"]) == 6


def test_regla_r4_sin_datos_subcanal(client):
    """R4 debe reportar sin datos cuando no se puede separar por subcanal."""
    client.login()
    resp = client.get("/api/regla-r4")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["regla"] == "R4"
    assert data["datos"]["resumen"]["subcanales_sin_datos"] == 2


def test_regla_r5_sin_asesores_sin_inventar(client):
    """R5 debe reportar asesores vacíos cuando no hay columna de subcanal."""
    client.login()
    resp = client.get("/api/regla-r5")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["regla"] == "R5"
    assert data["datos"]["asesores"] == []
    assert data["datos"]["resumen"]["total_asesores"] == 0


def test_agente_ia_sin_api_key(client):
    """El agente de IA debe devolver error estructurado sin IA_API_KEY."""
    client.login()
    resp = client.post("/api/agente-ia",
                       data=json.dumps({"canales": [], "buzones": [], "matriz_asesor_buzon": {},
                                        "subcanales_whatsapp": [], "desempeno_asesores": [],
                                        "metadata": {}}),
                       content_type="application/json")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["error"] is True
    assert data["codigo"] == "IA_API_KEY_NO_CONFIGURADA"


def test_endpoint_descargar(client):
    """El endpoint /api/descargar debe devolver Markdown."""
    client.login()
    resp = client.get("/api/descargar")
    assert resp.status_code == 200
    assert "text/markdown" in resp.content_type
