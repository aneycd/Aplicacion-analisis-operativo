"""
Servicio de lectura de insumos.
Lee los archivos Excel de la carpeta insumos/ y devuelve metadatos
(columnas, número de filas, muestra de datos) sin modificar nada.
Regla R6: fidelidad absoluta, solo lectura, nada se inventa.
"""

from pathlib import Path
from openpyxl import load_workbook


INSUMOS_DIR = Path(__file__).resolve().parent.parent.parent / "insumos"


def listar_archivos_insumos():
    """Devuelve la lista de archivos .xlsx en la carpeta insumos/."""
    if not INSUMOS_DIR.exists():
        return []
    return sorted(INSUMOS_DIR.glob("*.xlsx"))


def leer_excel(ruta_archivo):
    """
    Lee un archivo Excel y devuelve información por hoja:
    - nombre de hoja
    - max_row, max_column
    - filas de datos detectadas (después del encabezado)
    - encabezados detectados
    - muestra de las primeras 2 filas de datos
    Usa read_only=True para leer archivos grandes de forma eficiente.
    """
    wb = load_workbook(str(ruta_archivo), data_only=True, read_only=True)
    resultado = {
        "archivo": ruta_archivo.name,
        "hojas": []
    }
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        hoja_info = {
            "nombre": sheet_name,
            "max_row": ws.max_row,
            "max_column": ws.max_column,
            "encabezados": [],
            "filas_datos": 0,
            "muestra": []
        }

        # Detectar fila de encabezados (primera fila con >= 2 celdas no vacías)
        # En modo read_only, iteramos sobre las primeras 10 filas
        fila_encabezados = None
        encabezados = []
        for row_idx, row in enumerate(ws.iter_rows(min_row=1, max_row=10, values_only=True), start=1):
            celdas_no_vacias = [(i, v) for i, v in enumerate(row)
                                if v is not None and str(v).strip() != ""]
            if len(celdas_no_vacias) >= 2:
                fila_encabezados = row_idx
                encabezados = [(i, str(v)) for i, v in celdas_no_vacias]
                break

        if fila_encabezados:
            hoja_info["encabezados"] = encabezados
            hoja_info["fila_encabezados"] = fila_encabezados

            # Contar filas de datos después del encabezado (límite para evitar lentitud)
            filas_datos = 0
            muestra = []
            for row in ws.iter_rows(min_row=fila_encabezados + 1, values_only=True):
                if any(cell is not None and str(cell).strip() != "" for cell in row):
                    filas_datos += 1
                    if len(muestra) < 2:
                        muestra.append([str(v) if v is not None else "" for v in row])
            hoja_info["filas_datos"] = filas_datos
            hoja_info["muestra"] = muestra

        resultado["hojas"].append(hoja_info)

    wb.close()
    return resultado


def leer_todos_los_insumos():
    """Lee todos los archivos Excel de insumos/ y devuelve metadatos combinados."""
    archivos = listar_archivos_insumos()
    resultado = []
    for archivo in archivos:
        resultado.append(leer_excel(archivo))
    return resultado


def _fila_tiene_contenido(fila):
    """Devuelve True si la fila tiene al menos una celda no vacía."""
    return any(cell is not None and str(cell).strip() != "" for cell in fila)


def _primer_encabezado_valido(ws):
    """
    Encuentra la primera fila que parece encabezado de datos
    (tiene al menos 3 celdas no vacías con texto).
    Devuelve (lista_de_encabezados, numero_de_fila) o ([], 0) si no se encuentra.
    """
    for row_idx in range(1, min(ws.max_row + 1, 20)):
        fila = [c.value for c in ws[row_idx]]
        celdas_no_vacias = [str(v).strip() for v in fila if v is not None and str(v).strip() != ""]
        if len(celdas_no_vacias) >= 3:
            return celdas_no_vacias, row_idx
    return [], 0
