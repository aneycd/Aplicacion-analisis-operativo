# tests/test_regla_r1_metricas_canal.py
# Pruebas de unidad para la regla de negocio R1: métricas globales por canal.
# Verifica estructura, consistencia y cumplimiento de la regla R6 (no inventar datos).

import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.services.regla_r1_metricas_canal import metricas_globales_por_canal


def test_r1_devuelve_lista_de_canales():
    """La regla R1 debe devolver una lista de 4 canales."""
    resultado = metricas_globales_por_canal()
    assert isinstance(resultado, list), "El resultado debe ser una lista"
    assert len(resultado) == 4, f"Se esperaban 4 canales, se obtuvieron {len(resultado)}"


def test_r1_tiene_4_canales_esperados():
    """La regla R1 debe procesar exactamente 4 canales definidos en AGENTS.md."""
    resultado = metricas_globales_por_canal()
    canales_esperados = {"Chatbot/CORI", "Llamadas", "Correos", "WhatsApp/Redes Sociales"}
    canales_obtenidos = {c["canal"] for c in resultado}
    assert canales_obtenidos == canales_esperados, (
        f"Se esperaban canales {canales_esperados}, se obtuvieron {canales_obtenidos}"
    )


def test_r1_cada_canal_tiene_claves_requeridas():
    """Cada canal del resultado R1 debe tener las claves del contrato."""
    resultado = metricas_globales_por_canal()
    claves_requeridas = {"canal", "cantidad_atendida", "aht", "tr", "gestiones_asesor", "origen"}
    for canal in resultado:
        claves_obtenidas = set(canal.keys())
        faltantes = claves_requeridas - claves_obtenidas
        assert not faltantes, f"Faltan claves en canal '{canal.get('canal')}': {faltantes}"


def test_r1_chatbot_tiene_datos_reales():
    """Chatbot/CORI debe tener datos reales (no DATO FALTANTE) porque el insumo tiene métricas."""
    resultado = metricas_globales_por_canal()
    cb = next((c for c in resultado if c["canal"] == "Chatbot/CORI"), None)
    assert cb is not None, "Debe existir el canal Chatbot/CORI"
    assert cb["cantidad_atendida"] != "DATO FALTANTE", "Chatbot/CORI debe tener cantidad atendida"
    assert cb["aht"] != "DATO FALTANTE", "Chatbot/CORI debe tener AHT"
    assert isinstance(cb["cantidad_atendida"], int)
    assert cb["cantidad_atendida"] > 0


def test_r1_no_inventa_datos_para_canales_sin_insumo():
    """Los canales sin datos en insumos deben reportar DATO FALTANTE (regla R6)."""
    resultado = metricas_globales_por_canal()
    for canal in resultado:
        if canal["canal"] != "Chatbot/CORI":
            assert canal["cantidad_atendida"] == "DATO FALTANTE", (
                f"{canal['canal']} debe reportar DATO FALTANTE, no inventar valor"
            )
            assert canal["aht"] == "DATO FALTANTE"
            assert canal["tr"] == "DATO FALTANTE"


def test_r1_gestiones_asesor_es_lista():
    """Cada canal debe tener gestiones_asesor como una lista."""
    resultado = metricas_globales_por_canal()
    for canal in resultado:
        assert isinstance(canal["gestiones_asesor"], list), (
            f"gestiones_asesor de '{canal['canal']}' debe ser una lista"
        )
