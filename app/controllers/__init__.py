"""
Controladores de la aplicación.
Define el blueprint principal con las rutas de la app.
Incluye control de acceso por login (usuario administrador por variables de entorno).
"""

import hmac
import os
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, flash

from app.services.lectura_insumos import leer_todos_los_insumos, INSUMOS_DIR
from app.services.regla_r1_metricas_canal import metricas_globales_por_canal
from app.services.regla_r2_correos_buzon import correos_por_buzon
from app.services.regla_r3_matriz_asesor_buzon import calcular_matriz_asesor_buzon
from app.services.regla_r4_whatsapp_subcanal import calcular_whatsapp_por_subcanal
from app.services.regla_r5_whatsapp_asesor import calcular_desempeño_asesor_whatsapp
from app.services.agente_ia import procesar_con_agente_ia

main_bp = Blueprint("main", __name__)


def login_requerido(func):
    """Decorador que exige haber iniciado sesión para acceder a una ruta.
    Si no hay sesión activa, redirige a /login."""
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("usuario_autenticado"):
            return redirect(url_for("main.login"))
        return func(*args, **kwargs)
    return wrapper


# ==================== RUTAS DE AUTENTICACIÓN ====================

@main_bp.route("/login", methods=["GET"])
def login():
    """Pantalla de login: formulario con usuario y contraseña."""
    if session.get("usuario_autenticado"):
        return redirect(url_for("main.inicio"))
    error = request.args.get("error")
    return render_template("login.html", error=error)


@main_bp.route("/login", methods=["POST"])
def login_post():
    """Procesa el login: compara con APP_USUARIO y APP_CLAVE usando hmac.compare_digest."""
    usuario = request.form.get("usuario", "")
    clave = request.form.get("clave", "")

    app_usuario = os.environ.get("APP_USUARIO", "")
    app_clave = os.environ.get("APP_CLAVE", "")

    # Usar hmac.compare_digest para comparación segura contra timing attacks
    usuario_correcto = hmac.compare_digest(usuario, app_usuario or "")
    clave_correcta = hmac.compare_digest(clave, app_clave or "")

    if usuario_correcto and clave_correcta:
        session.permanent = True
        session["usuario_autenticado"] = True
        session["usuario_nombre"] = usuario
        return redirect(url_for("main.inicio"))
    else:
        # No revelar cuál de los dos falló
        return redirect(url_for("main.login", error="1"))


@main_bp.route("/salir")
def salir():
    """Borra la sesión y redirige a /login."""
    session.clear()
    return redirect(url_for("main.login"))


# ==================== RUTAS PROTEGIDAS ====================

@main_bp.route("/")
@login_requerido
def inicio():
    """Pantalla de inicio: formulario para cargar/seleccionar insumos."""
    return render_template("inicio.html")


@main_bp.route("/resultados")
@login_requerido
def resultados():
    """Pantalla de resultados: tablero con contadores y tablas."""
    return render_template("resultados.html")


@main_bp.route("/detalle")
@login_requerido
def detalle():
    """Pantalla de detalle por registro/asesor."""
    return render_template("detalle.html")


@main_bp.route("/api/health")
def health():
    """Endpoint de salud para verificar que la app responde."""
    return jsonify({"status": "ok", "mensaje": "App de análisis operativo Contact Center"})


@main_bp.route("/api/insumos")
@login_requerido
def insumos():
    """Devuelve metadatos de todos los archivos Excel en insumos/ (solo lectura)."""
    try:
        datos = leer_todos_los_insumos()
        return jsonify({"status": "ok", "insumos": datos})
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)}), 500


@main_bp.route("/api/regla-r1")
@login_requerido
def regla_r1():
    """Ejecuta la regla de negocio R1: métricas globales por canal."""
    try:
        datos = metricas_globales_por_canal()
        return jsonify({"status": "ok", "regla": "R1", "datos": datos})
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)}), 500


@main_bp.route("/api/regla-r2")
@login_requerido
def regla_r2():
    """Ejecuta la regla de negocio R2: desglose de correos por buzón."""
    try:
        datos = correos_por_buzon()
        return jsonify({"status": "ok", "regla": "R2", "datos": datos})
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)}), 500


@main_bp.route("/api/regla-r3")
@login_requerido
def regla_r3():
    """Ejecuta la regla de negocio R3: matriz Asesor vs Buzón."""
    try:
        datos = calcular_matriz_asesor_buzon(str(INSUMOS_DIR))
        return jsonify({"status": "ok", "regla": "R3", "datos": datos})
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)}), 500


@main_bp.route("/api/regla-r4")
@login_requerido
def regla_r4():
    """Ejecuta la regla de negocio R4: WhatsApp por subcanal."""
    try:
        datos = calcular_whatsapp_por_subcanal(str(INSUMOS_DIR))
        return jsonify({"status": "ok", "regla": "R4", "datos": datos})
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)}), 500


@main_bp.route("/api/regla-r5")
@login_requerido
def regla_r5():
    """Ejecuta la regla de negocio R5: desempeño por asesor WhatsApp."""
    try:
        datos = calcular_desempeño_asesor_whatsapp(str(INSUMOS_DIR))
        return jsonify({"status": "ok", "regla": "R5", "datos": datos})
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)}), 500


@main_bp.route("/api/agente-ia", methods=["POST"])
@login_requerido
def agente_ia():
    """Ejecuta el agente de IA con los datos de las reglas R1-R5."""
    try:
        from flask import request
        entrada = request.get_json(force=True) or {}
        entrada_completa = {
            "canales": entrada.get("canales", []),
            "buzones": entrada.get("buzones", []),
            "matriz_asesor_buzon": entrada.get("matriz_asesor_buzon", {}),
            "subcanales_whatsapp": entrada.get("subcanales_whatsapp", []),
            "desempeno_asesores": entrada.get("desempeno_asesores", []),
            "metadata": {
                "archivo": "insumos/",
                "fecha": "",
            },
        }
        resultado = procesar_con_agente_ia(entrada_completa)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)}), 500


@main_bp.route("/api/descargar")
@login_requerido
def descargar():
    """Endpoint para descargar el informe (Markdown)."""
    from flask import make_response
    informe = "# Informe Ejecutivo\n\nEste es un informe de ejemplo. Configura IA_API_KEY en .env para generar el informe completo con el agente de IA."
    response = make_response(informe)
    response.headers["Content-Disposition"] = "attachment; filename=informe_ejecutivo.md"
    response.headers["Content-Type"] = "text/markdown; charset=utf-8"
    return response


@main_bp.route("/api/informe")
@login_requerido
def informe_consolidado():
    """Endpoint consolidado que devuelve todas las reglas de negocio (R1-R5) en una sola respuesta."""
    try:
        from app.services.regla_r1_metricas_canal import metricas_globales_por_canal
        from app.services.regla_r2_correos_buzon import correos_por_buzon
        from app.services.regla_r3_matriz_asesor_buzon import calcular_matriz_asesor_buzon
        from app.services.regla_r4_whatsapp_subcanal import calcular_whatsapp_por_subcanal
        from app.services.regla_r5_whatsapp_asesor import calcular_desempeño_asesor_whatsapp

        return jsonify({
            "status": "ok",
            "r1_metricas_canal": {
                "canales": metricas_globales_por_canal(),
                "resumen": {
                    "total_canales": 4,
                    "canales_con_datos": sum(1 for c in metricas_globales_por_canal() if c["cantidad_atendida"] != "DATO FALTANTE"),
                    "canales_sin_datos": sum(1 for c in metricas_globales_por_canal() if c["cantidad_atendida"] == "DATO FALTANTE"),
                }
            },
            "r2_correos_buzon": {
                **correos_por_buzon(),
                "resumen": {
                    "total_buzones": 6,
                    "buzones_encontrados": 0,
                    "buzones_no_encontrados": 6,
                }
            },
            "r3_matriz_asesor_buzon": calcular_matriz_asesor_buzon(str(INSUMOS_DIR)),
            "r4_whatsapp_subcanal": calcular_whatsapp_por_subcanal(str(INSUMOS_DIR)),
            "r5_desempeno_asesor": calcular_desempeño_asesor_whatsapp(str(INSUMOS_DIR)),
        })
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)}), 500
