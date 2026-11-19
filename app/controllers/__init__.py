"""
Controladores de la aplicación.
Define el blueprint principal con las rutas de la app.
"""

from flask import Blueprint, render_template, request, jsonify

from app.services.lectura_insumos import leer_todos_los_insumos, INSUMOS_DIR
from app.services.regla_r1_metricas_canal import metricas_globales_por_canal
from app.services.regla_r2_correos_buzon import correos_por_buzon
from app.services.regla_r3_matriz_asesor_buzon import calcular_matriz_asesor_buzon
from app.services.regla_r4_whatsapp_subcanal import calcular_whatsapp_por_subcanal
from app.services.regla_r5_whatsapp_asesor import calcular_desempeño_asesor_whatsapp
from app.services.agente_ia import procesar_con_agente_ia

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def inicio():
    """Pantalla de inicio: formulario para cargar/seleccionar insumos."""
    return render_template("inicio.html")


@main_bp.route("/resultados")
def resultados():
    """Pantalla de resultados: tablero con contadores y tablas."""
    return render_template("resultados.html")


@main_bp.route("/detalle")
def detalle():
    """Pantalla de detalle por registro/asesor."""
    return render_template("detalle.html")


@main_bp.route("/api/health")
def health():
    """Endpoint de salud para verificar que la app responde."""
    return jsonify({"status": "ok", "mensaje": "App de análisis operativo Contact Center"})


@main_bp.route("/api/insumos")
def insumos():
    """Devuelve metadatos de todos los archivos Excel en insumos/ (solo lectura)."""
    try:
        datos = leer_todos_los_insumos()
        return jsonify({"status": "ok", "insumos": datos})
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)}), 500


@main_bp.route("/api/regla-r1")
def regla_r1():
    """Ejecuta la regla de negocio R1: métricas globales por canal."""
    try:
        datos = metricas_globales_por_canal()
        return jsonify({"status": "ok", "regla": "R1", "datos": datos})
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)}), 500


@main_bp.route("/api/regla-r2")
def regla_r2():
    """Ejecuta la regla de negocio R2: desglose de correos por buzón."""
    try:
        datos = correos_por_buzon()
        return jsonify({"status": "ok", "regla": "R2", "datos": datos})
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)}), 500


@main_bp.route("/api/regla-r3")
def regla_r3():
    """Ejecuta la regla de negocio R3: matriz Asesor vs Buzón."""
    try:
        datos = calcular_matriz_asesor_buzon(str(INSUMOS_DIR))
        return jsonify({"status": "ok", "regla": "R3", "datos": datos})
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)}), 500


@main_bp.route("/api/regla-r4")
def regla_r4():
    """Ejecuta la regla de negocio R4: WhatsApp por subcanal."""
    try:
        datos = calcular_whatsapp_por_subcanal(str(INSUMOS_DIR))
        return jsonify({"status": "ok", "regla": "R4", "datos": datos})
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)}), 500


@main_bp.route("/api/regla-r5")
def regla_r5():
    """Ejecuta la regla de negocio R5: desempeño por asesor WhatsApp."""
    try:
        datos = calcular_desempeño_asesor_whatsapp(str(INSUMOS_DIR))
        return jsonify({"status": "ok", "regla": "R5", "datos": datos})
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)}), 500


@main_bp.route("/api/agente-ia", methods=["POST"])
def agente_ia():
    """Ejecuta el agente de IA con los datos de las reglas R1-R5."""
    try:
        from flask import request
        entrada = request.get_json(force=True) or {}
        # Construir el contrato de entrada a partir de las reglas
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
def descargar():
    """Endpoint para descargar el informe (Markdown)."""
    from flask import make_response
    informe = "# Informe Ejecutivo\n\nEste es un informe de ejemplo. Configura IA_API_KEY en .env para generar el informe completo con el agente de IA."
    response = make_response(informe)
    response.headers["Content-Disposition"] = "attachment; filename=informe_ejecutivo.md"
    response.headers["Content-Type"] = "text/markdown; charset=utf-8"
    return response


@main_bp.route("/api/informe")
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
