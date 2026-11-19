"""
Pruebas de integración para el control de acceso por login.
Valida:
1. Entrar con usuario y contraseña correctos
2. Entrar con clave equivocada
3. Acceder a pantalla principal sin haber entrado (redirige a /login)
4. Salir y volver a intentar entrar a la pantalla principal
"""

import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "clave-de-prueba-para-tests"
    with app.test_client() as client:
        yield client


def test_login_con_credenciales_correctas(client):
    """Debe permitir entrar con usuario y contraseña correctos."""
    # Primero ir a /login para obtener la página
    resp = client.get("/login")
    assert resp.status_code == 200

    # Enviar credenciales correctas
    resp = client.post("/login", data={
        "usuario": "admin",
        "clave": "Cambiar2026"
    }, follow_redirects=False)
    assert resp.status_code == 302  # Redirección a inicio
    assert resp.headers["Location"].endswith("/")

    # Verificar que ahora se puede acceder a /
    with client.session_transaction() as sess:
        assert sess.get("usuario_autenticado") is True

    resp = client.get("/")
    assert resp.status_code == 200


def test_login_con_clave_equivocada(client):
    """No debe permitir entrar con clave equivocada."""
    resp = client.post("/login", data={
        "usuario": "admin",
        "clave": "clave-incorrecta"
    }, follow_redirects=False)
    assert resp.status_code == 302  # Redirección a /login con error
    assert "/login" in resp.headers["Location"]

    # No debe haber sesión activa
    with client.session_transaction() as sess:
        assert sess.get("usuario_autenticado") is not True


def test_pantalla_principal_sin_entrada_redirige_a_login(client):
    """Acceder a / sin haber entrado debe redirigir a /login."""
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")


def test_salir_y_volver_a_intentar_entrar(client):
    """Después de salir, no se puede acceder a / y se debe entrar de nuevo."""
    # Entrar primero
    client.post("/login", data={
        "usuario": "admin",
        "clave": "Cambiar2026"
    })

    # Verificar que está autenticado
    with client.session_transaction() as sess:
        assert sess.get("usuario_autenticado") is True

    # Salir
    resp = client.get("/salir", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")

    # Verificar que la sesión se borró
    with client.session_transaction() as sess:
        assert sess.get("usuario_autenticado") is not True

    # Intentar acceder a / sin entrar de nuevo
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")

    # Entrar de nuevo con credenciales correctas
    resp = client.post("/login", data={
        "usuario": "admin",
        "clave": "Cambiar2026"
    }, follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/")

    # Verificar que ahora sí se puede acceder
    resp = client.get("/")
    assert resp.status_code == 200


def test_rutas_api_requieren_login(client):
    """Los endpoints de API deben requerir autenticación."""
    resp = client.get("/api/health", follow_redirects=False)
    # /api/health no requiere login (es público para health check)
    # Pero los demás sí. Verificamos /api/insumos
    resp = client.get("/api/insumos", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")
