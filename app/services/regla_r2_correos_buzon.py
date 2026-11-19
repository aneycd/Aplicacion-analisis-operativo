"""
Regla de negocio R2 — Desglose de correos por buzón.

Lee el insumo de llamadas y correos y extrae la cantidad atendida
por cada uno de los 6 buzones definidos en AGENTS.md.

Regla R6: si un buzón no aparece en los insumos, se reporta como
"DATO FALTANTE" sin inventar valor.
"""

from pathlib import Path
from openpyxl import load_workbook

INSUMOS_DIR = Path(__file__).resolve().parent.parent.parent / "insumos"

BUZONES_ESPERADOS = [
    "Bienes adquiridos",
    "Centro Asistencia N1",
    "Centro Asistencia N2",
    "Operativa CAC PCI",
    "Servicio oficina virtual",
    "Soporte CAC",
]


def _seguro_int(valor):
    if valor is None:
        return 0
    try:
        return int(float(valor))
    except (ValueError, TypeError):
        return 0


def correos_por_buzon():
    """
    Devuelve la cantidad atendida por cada buzón de correos.
    Usa read_only=True para leer archivos grandes de forma eficiente.
    """
    archivo = INSUMOS_DIR / "Control llamadas y correos.xlsx"
    if not archivo.exists():
        return {
            "regla": "R2",
            "buzones": [
                {"buzon": b, "cantidad": "DATO FALTANTE", "origen": "archivo no encontrado"}
                for b in BUZONES_ESPERADOS
            ],
        }

    # Cargar en modo read_only para archivos grandes
    wb = load_workbook(str(archivo), data_only=True, read_only=True)

    resultado_buzones = []
    encontrado = False

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]

        # Buscar fila de encabezados (primeras 10 filas)
        fila_enc = None
        for row_idx, row in enumerate(ws.iter_rows(min_row=1, max_row=10, values_only=True), start=1):
            texto_fila = " ".join(
                str(v).strip().lower() for v in row if v is not None
            )
            palabras_clave = ["buzon", "buzón", "correo", "canal", "nivel", "cantidad", "atendida"]
            coincidencias = sum(1 for p in palabras_clave if p in texto_fila)
            if coincidencias >= 2:
                fila_enc = row_idx
                encabezados = [str(v).strip().lower() if v is not None else "" for v in row]
                break

        if fila_enc is None:
            continue

        # Encontrar índices de columnas relevantes
        col_buzon = None
        col_cant = None
        for i, h in enumerate(encabezados):
            if any(p in h for p in ["buzon", "buzón", "nivel"]):
                col_buzon = i
            if any(p in h for p in ["cantidad", "atendida", "contestadas"]):
                col_cant = i

        if col_buzon is None:
            continue

        encontrado = True
        cantidades = {b: 0 for b in BUZONES_ESPERADOS}

        for row in ws.iter_rows(min_row=fila_enc + 1, values_only=True):
            if not any(cell is not None and str(cell).strip() != "" for cell in row):
                continue
            valor_buzon = str(row[col_buzon]).strip() if col_buzon < len(row) and row[col_buzon] else ""
            cantidad = _seguro_int(row[col_cant]) if col_cant is not None and col_cant < len(row) else 0
            for b in BUZONES_ESPERADOS:
                if b.lower() in valor_buzon.lower():
                    cantidades[b] += cantidad

        for b in BUZONES_ESPERADOS:
            resultado_buzones.append({
                "buzon": b,
                "cantidad": cantidades[b] if cantidades[b] > 0 else "DATO FALTANTE",
                "origen": f"{archivo.name} - hoja {sheet_name}",
            })
        break

    wb.close()

    if not encontrado:
        resultado_buzones = [
            {"buzon": b, "cantidad": "DATO FALTANTE", "origen": "no se encontró columna de buzón en insumos"}
            for b in BUZONES_ESPERADOS
        ]

    return {
        "regla": "R2",
        "buzones": resultado_buzones,
    }
