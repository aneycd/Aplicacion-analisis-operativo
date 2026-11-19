"""
Regla de negocio R1 — Métricas globales por canal.

Lee los datos crudos de los 3 archivos Excel y calcula para cada canal:
- Cantidad Atendida (contestadas/atendidas)
- AHT (Average Handling Time)
- TR (Tasa de Respuesta / Tasa de Servicio)
- Gestiones por Asesor

Regla R6: fidelidad absoluta. Si un dato no existe en el insumo, se reporta
como "DATO FALTANTE" sin inventar valor.
"""

from pathlib import Path
from openpyxl import load_workbook

INSUMOS_DIR = Path(__file__).resolve().parent.parent.parent / "insumos"


def _seguro_float(valor):
    """Convierte un valor a float de forma segura. Retorna None si no es convertible."""
    if valor is None:
        return None
    try:
        return float(valor)
    except (ValueError, TypeError):
        return None


def _seguro_int(valor):
    """Convierte un valor a int de forma segura. Retorna None si no es convertible."""
    if valor is None:
        return None
    try:
        return int(float(valor))
    except (ValueError, TypeError):
        return None


def _buscar_fila_encabezados_datos(ws):
    """
    Encuentra la fila de encabezados de datos buscando palabras clave
    como 'agente', 'contestadas', 'aht'. Evita confundir con filas de
    metadatos (como 'Nivel', 'N1', 'Mes', etc.).
    """
    palabras_clave = ["agente", "contestadas", "atendidas", "aht", "ofrecidas"]
    for row_idx in range(1, min(ws.max_row + 1, 15)):
        fila = [c.value for c in ws[row_idx]]
        texto_fila = " ".join(
            str(v).strip().lower() for v in fila if v is not None
        )
        coincidencias = sum(1 for p in palabras_clave if p in texto_fila)
        if coincidencias >= 2:
            return row_idx
    return None


def _extraer_columnas_por_nombre(ws, fila_enc, nombres_buscados):
    """
    Dada una hoja y la fila de encabezados, devuelve un diccionario
    {nombre_columna: índice_de_columna} para las columnas que coincidan
    con los nombres buscados (búsqueda case-insensitive, ignorando espacios).
    """
    encabezados = {}
    for col_idx in range(1, ws.max_column + 1):
        celda = ws.cell(row=fila_enc, column=col_idx).value
        if celda is not None:
            clave = str(celda).strip().lower()
            for nombre in nombres_buscados:
                if nombre.strip().lower() in clave:
                    encabezados[nombre.strip().lower()] = col_idx - 1  # base 0
    return encabezados


def metrica_chatbot_corri():
    """
    Extrae métricas del canal Chatbot/CORI desde Control CHATBOT.xlsx, hoja 'Chat'.
    """
    archivo = INSUMOS_DIR / "Control CHATBOT.xlsx"
    if not archivo.exists():
        return {
            "canal": "Chatbot/CORI",
            "cantidad_atendida": "DATO FALTANTE",
            "aht": "DATO FALTANTE",
            "tr": "DATO FALTANTE",
            "gestiones_asesor": [],
            "origen": "archivo no encontrado",
        }

    wb = load_workbook(str(archivo), data_only=True)
    if "Chat" not in wb.sheetnames:
        wb.close()
        return {
            "canal": "Chatbot/CORI",
            "cantidad_atendida": "DATO FALTANTE",
            "aht": "DATO FALTANTE",
            "tr": "DATO FALTANTE",
            "gestiones_asesor": [],
            "origen": "hoja 'Chat' no encontrada",
        }

    ws = wb["Chat"]
    fila_enc = _buscar_fila_encabezados_datos(ws)
    if not fila_enc:
        wb.close()
        return {
            "canal": "Chatbot/CORI",
            "cantidad_atendida": "DATO FALTANTE",
            "aht": "DATO FALTANTE",
            "tr": "DATO FALTANTE",
            "gestiones_asesor": [],
            "origen": "no se detectaron encabezados",
        }

    # Buscar columnas por nombres conocidos en la hoja Chat
    cols = _extraer_columnas_por_nombre(
        ws, fila_enc,
        ["agente", "contestadas", "aht", "%tr", "ofrecidas"]
    )

    total_atendidas = 0
    total_aht = 0.0
    count_aht = 0
    gestiones_asesor = []

    for row in ws.iter_rows(min_row=fila_enc + 1, values_only=True):
        if not any(cell is not None and str(cell).strip() != "" for cell in row):
            continue

        agente_idx = cols.get("agente")
        contestadas_idx = cols.get("contestadas")
        aht_idx = cols.get("aht")
        tr_idx = cols.get("%tr")

        agente = str(row[agente_idx]).strip() if agente_idx is not None and agente_idx < len(row) and row[agente_idx] else "Desconocido"
        contestadas = _seguro_int(row[contestadas_idx]) if contestadas_idx is not None and contestadas_idx < len(row) else 0
        aht = _seguro_float(row[aht_idx]) if aht_idx is not None and aht_idx < len(row) else None
        tr = _seguro_float(row[tr_idx]) if tr_idx is not None and tr_idx < len(row) else None

        if contestadas and contestadas > 0:
            total_atendidas += contestadas
        if aht is not None:
            total_aht += aht
            count_aht += 1

        gestiones_asesor.append({
            "asesor": agente,
            "gestiones": contestadas if contestadas else 0,
        })

    wb.close()

    aht_promedio = round(total_aht / count_aht, 2) if count_aht > 0 else "DATO FALTANTE"
    # TR: usamos el primer valor válido encontrado o promedio
    tr_valores = [g for g in gestiones_asesor if g.get("tr") is not None]

    return {
        "canal": "Chatbot/CORI",
        "cantidad_atendida": total_atendidas if total_atendidas > 0 else "DATO FALTANTE",
        "aht": aht_promedio,
        "tr": "DATO FALTANTE",  # Se calculará con más detalle cuando se confirme la columna exacta
        "gestiones_asesor": gestiones_asesor,
        "origen": "Control CHATBOT.xlsx - hoja Chat",
    }


def metricas_globales_por_canal():
    """
    Devuelve métricas para los 4 canales definidos en AGENTS.md.
    Cada canal usa su archivo de insumo correspondiente.
    """
    canales = [
        metrica_chatbot_corri(),
        {
            "canal": "Llamadas",
            "cantidad_atendida": "DATO FALTANTE",
            "aht": "DATO FALTANTE",
            "tr": "DATO FALTANTE",
            "gestiones_asesor": [],
            "origen": "pendiente de implementar detalle por hoja",
        },
        {
            "canal": "Correos",
            "cantidad_atendida": "DATO FALTANTE",
            "aht": "DATO FALTANTE",
            "tr": "DATO FALTANTE",
            "gestiones_asesor": [],
            "origen": "pendiente de implementar detalle por hoja",
        },
        {
            "canal": "WhatsApp/Redes Sociales",
            "cantidad_atendida": "DATO FALTANTE",
            "aht": "DATO FALTANTE",
            "tr": "DATO FALTANTE",
            "gestiones_asesor": [],
            "origen": "pendiente de implementar detalle por hoja",
        },
    ]
    return canales
