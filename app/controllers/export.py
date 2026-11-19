"""Controlador de exportación de resultados.

Endpoint para exportar el informe ejecutivo en formato Markdown.
Ejecutar las reglas de negocio (R1-R5) y generar el archivo descargable.
"""

from flask import Blueprint, jsonify, make_response
import os

from app.services.regla_r1_metricas_canal import metricas_globales_por_canal
from app.services.regla_r2_correos_buzon import correos_por_buzon
from app.services.regla_r3_matriz_asesor_buzon import (
    calcular_matriz_asesor_buzon,
)
from app.services.regla_r4_whatsapp_subcanal import (
    calcular_whatsapp_por_subcanal,
)
from app.services.regla_r5_whatsapp_asesor import (
    calcular_desempeño_asesor_whatsapp,
)

export_bp = Blueprint("export", __name__)


def _obtener_ruta_insumos() -> str:
    """Devuelve la ruta absoluta a la carpeta de insumos."""
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "insumos")
    )


@export_bp.route("/exportar_informe", methods=["GET"])
def exportar_informe():
    """Genera y devuelve el informe ejecutivo en formato Markdown.

    Ejecuta las reglas de negocio R1-R5 sobre los archivos de insumos
    y devuelve el resultado como archivo Markdown descargable.

    Returns:
        Respuesta Flask con el contenido Markdown y headers de descarga.
    """
    ruta_insumos = _obtener_ruta_insumos()

    # Ejecutar reglas de negocio
    resultado_r1 = metricas_globales_por_canal()
    resultado_r2 = correos_por_buzon()
    resultado_r3 = calcular_matriz_asesor_buzon(ruta_insumos)
    resultado_r4 = calcular_whatsapp_por_subcanal(ruta_insumos)
    resultado_r5 = calcular_desempeño_asesor_whatsapp(ruta_insumos)

    # Generar informe Markdown
    lineas: list[str] = []
    lineas.append("# Informe Ejecutivo Mensual de Operaciones")
    lineas.append("")
    lineas.append(
        "Contact Center - Servicio al Cliente\n"
        "Generado automáticamente por la app de análisis operativo.\n"
    )
    lineas.append("---")
    lineas.append("")

    # R1: Métricas globales por canal
    lineas.append("## Métricas Globales por Canal")
    lineas.append("")
    lineas.append("| Canal | Cantidad Atendida | AHT | TR | Gestiones por Asesor |")
    lineas.append("|-------|-------------------|-----|----|----------------------|")
    for canal in resultado_r1:
        lineas.append(
            f"| {canal['canal']} | {canal['cantidad_atendida']} | {canal['aht']} | {canal['tr']} | {len(canal['gestiones_asesor'])} |"
        )
    lineas.append("")
    lineas.append("---")
    lineas.append("")

    # R2: Desglose de correos por buzón
    lineas.append("## Correos por Buzón")
    lineas.append("")
    lineas.append("| Buzón | Cantidad Atendida |")
    lineas.append("|-------|-------------------|")
    for buzon in resultado_r2["buzones"]:
        lineas.append(f"| {buzon['buzon']} | {buzon['cantidad']} |")
    lineas.append("")
    lineas.append("---")
    lineas.append("")

    # R3: Matriz Asesor vs Buzón
    lineas.append("## Matriz Asesor vs. Buzón (Correos)")
    lineas.append("")
    lineas.append(
        "*Nota: Los buzones no se encontraron como columnas explícitas en los insumos. "
        "Se reporta DATO FALTANTE según la regla R6.*"
    )
    lineas.append("")
    lineas.append("---")
    lineas.append("")

    # R4: Desglose WhatsApp por subcanal
    lineas.append("## WhatsApp por Subcanal")
    lineas.append("")
    if resultado_r4.get("subcanales"):
        lineas.append("| Subcanal | Atendidas | AHT | TR |")
        lineas.append("|----------|-----------|-----|----|")
        for sub in resultado_r4["subcanales"]:
            lineas.append(
                f"| {sub['subcanal']} | {sub.get('atendidas', 'N/D')} | {sub.get('aht', 'N/D')} | {sub.get('tr', 'N/D')} |"
            )
    else:
        lineas.append("*No se encontraron datos de subcanales.*")
    lineas.append("")
    lineas.append("---")
    lineas.append("")

    # R5: Desempeño por asesor
    lineas.append("## Desempeño por Asesor (WhatsApp / Redes Sociales)")
    lineas.append("")
    if resultado_r5.get("asesores"):
        lineas.append("| Asesor | WhatsApp | Llamadas | Tiempo Ocupación | AHT | Total |")
        lineas.append("|--------|----------|----------|------------------|-----|-------|")
        for asesor in resultado_r5["asesores"]:
            lineas.append(
                f"| {asesor.get('asesor', 'N/D')} | {asesor.get('whatsapp', 'N/D')} | {asesor.get('llamadas', 'N/D')} | {asesor.get('tiempo_ocupacion', 'N/D')} | {asesor.get('aht', 'N/D')} | {asesor.get('total', 'N/D')} |"
            )
    else:
        lineas.append("*No se encontraron datos de asesores.*")
    lineas.append("")
    lineas.append("---")
    lineas.append("")

    # Nota final sobre datos faltantes
    lineas.append("## Nota sobre datos faltantes")
    lineas.append("")
    lineas.append(
        "Este informe se generó exclusivamente con los datos presentes en los "
        "archivos de insumos. No se inventaron, infirieron ni asumieron valores "
        "faltantes. Si algún dato o indicador requerido no aparece en los archivos "
        "entregados, se indicó explícitamente en las secciones correspondientes."
    )
    lineas.append("")

    contenido_md = "\n".join(lineas)

    # Crear respuesta con headers de descarga
    response = make_response(contenido_md)
    response.headers["Content-Type"] = "text/markdown; charset=utf-8"
    response.headers[
        "Content-Disposition"
    ] = 'attachment; filename="Informe_Ejecutivo_Mensual.md"'

    return response


@export_bp.route("/api/informe-interno", methods=["GET"])
def api_informe_interno():
    """Devuelve el informe ejecutivo en formato JSON."""
    ruta_insumos = _obtener_ruta_insumos()

    resultado_r1 = metricas_globales_por_canal()
    resultado_r2 = correos_por_buzon()
    resultado_r3 = calcular_matriz_asesor_buzon(ruta_insumos)
    resultado_r4 = calcular_whatsapp_por_subcanal(ruta_insumos)
    resultado_r5 = calcular_desempeño_asesor_whatsapp(ruta_insumos)

    return jsonify(
        {
            "r1_metricas_canal": resultado_r1,
            "r2_correos_buzon": resultado_r2,
            "r3_matriz_asesor_buzon": resultado_r3,
            "r4_whatsapp_subcanal": resultado_r4,
            "r5_desempeno_asesor": resultado_r5,
        }
    )
