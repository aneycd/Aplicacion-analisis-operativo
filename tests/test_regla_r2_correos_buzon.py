# tests/test_regla_r2_correos_buzon.py
# Pruebas de unidad para la regla de negocio R2: desglose de correos por buzón.
# Verifica estructura, consistencia y cumplimiento de la regla R6 (no inventar datos).

import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.services.regla_r2_correos_buzon import correos_por_buzon, BUZONES_ESPERADOS


def test_r2_devuelve_estructura_correcta():
    """La regla R2 debe devolver un dict con claves 'regla' y 'buzones'."""
    resultado = correos_por_buzon()
    assert isinstance(resultado, dict), "El resultado debe ser un diccionario"
    assert "regla" in resultado, "Falta la clave 'regla'"
    assert "buzones" in resultado, "Falta la clave 'buzones'"
    assert resultado["regla"] == "R2"
    assert isinstance(resultado["buzones"], list), "'buzones' debe ser una lista"


def test_r2_tiene_6_buzones_del_contexto():
    """La regla R2 debe procesar exactamente los 6 buzones definidos en AGENTS.md."""
    resultado = correos_por_buzon()
    assert len(resultado["buzones"]) == len(BUZONES_ESPERADOS), (
        f"Se esperaban {len(BUZONES_ESPERADOS)} buzones, se obtuvieron {len(resultado['buzones'])}"
    )
    buzones_obtenidos = {b["buzon"] for b in resultado["buzones"]}
    assert buzones_obtenidos == set(BUZONES_ESPERADOS), (
        f"Buzones obtenidos no coinciden con AGENTS.md"
    )


def test_r2_cada_buzon_tiene_claves_requeridas():
    """Cada buzón del resultado R2 debe tener las claves del contrato."""
    resultado = correos_por_buzon()
    claves_requeridas = {"buzon", "cantidad", "origen"}
    for buzon in resultado["buzones"]:
        claves_obtenidas = set(buzon.keys())
        faltantes = claves_requeridas - claves_obtenidas
        assert not faltantes, f"Faltan claves en buzón '{buzon.get('buzon')}': {faltantes}"


def test_r2_no_inventa_cantidad_cuando_no_hay_columna():
    """Si no hay columna de buzón, cantidad debe ser DATO FALTANTE (regla R6)."""
    resultado = correos_por_buzon()
    for buzon in resultado["buzones"]:
        assert buzon["cantidad"] == "DATO FALTANTE", (
            f"{buzon['buzon']} debe reportar DATO FALTANTE, no inventar valor"
        )


def test_r2_origen_tiene_informacion():
    """Cada buzón debe tener información de origen (archivo y hoja)."""
    resultado = correos_por_buzon()
    for buzon in resultado["buzones"]:
        assert buzon["origen"] is not None
        assert len(buzon["origen"]) > 0
