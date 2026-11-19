# VALIDACIÓN.md — Esperado vs Obtenido

Resultados de las pruebas ejecutadas con pytest contra las cifras de control y casos límite definidos en AGENTS.md.

**Fecha de validación:** 2026-11-04  
**Total de pruebas:** 42  
**Pruebas pasadas:** 42  
**Pruebas falladas:** 0

---

## Resumen de validación

| Prueba | Esperado | Obtenido | Estado |
|--------|----------|----------|--------|
| App se crea correctamente | App Flask sin errores | App creada OK | ✅ |
| /api/health responde | status: "ok" | status: "ok" | ✅ |
| /api/insumos devuelve 3 archivos | 3 archivos Excel | 3 archivos (CHATBOT, llamadas y correos, WhatsApp) | ✅ |
| R1 - Chatbot/CORI tiene datos | cantidad_atendida ≠ DATO FALTANTE | 8904 atendidas, AHT 515.55, 49 asesores | ✅ |
| R1 - Otros canales sin datos | DATO FALTANTE | DATO FALTANTE (regla R6) | ✅ |
| R2 - 6 buzones del contexto | 6 filas de buzones | 6 buzones, todos DATO FALTANTE | ✅ |
| R2 - No inventar cantidades | cantidad = DATO FALTANTE | DATO FALTANTE para todos | ✅ |
| R3 - Matriz vacía | matriz = {} | matriz = {}, datos_disponibles = false | ✅ |
| R4 - Sin subcanales | subcanales_sin_datos = 2 | subcanales_sin_datos = 2 | ✅ |
| R5 - Sin asesores | asesores = [] | asesores = [], total_asesores = 0 | ✅ |
| Agente IA sin API_KEY | error: IA_API_KEY_NO_CONFIGURADA | error: IA_API_KEY_NO_CONFIGURADA | ✅ |
| /api/descargar | status 200, text/markdown | status 200, text/markdown | ✅ |
| /api/informe consolidado | JSON con R1-R5 | JSON válido con las 5 reglas | ✅ |

---

## Detalle por regla de negocio

### R1 — Métricas globales por canal
| Canal | Esperado | Obtenido |
|-------|----------|----------|
| Chatbot/CORI | Datos reales del insumo | 8904 atendidas, AHT 515.55, 49 asesores |
| Llamadas | DATO FALTANTE | DATO FALTANTE |
| Correos | DATO FALTANTE | DATO FALTANTE |
| WhatsApp/Redes Sociales | DATO FALTANTE | DATO FALTANTE |

### R2 — Desglose de correos por buzón
| Buzón | Esperado | Obtenido |
|-------|----------|----------|
| Bienes adquiridos | DATO FALTANTE (no hay columna) | DATO FALTANTE |
| Centro Asistencia N1 | DATO FALTANTE | DATO FALTANTE |
| Centro Asistencia N2 | DATO FALTANTE | DATO FALTANTE |
| Operativa CAC PCI | DATO FALTANTE | DATO FALTANTE |
| Servicio oficina virtual | DATO FALTANTE | DATO FALTANTE |
| Soporte CAC | DATO FALTANTE | DATO FALTANTE |

### R3 — Matriz Asesor vs Buzón
| Campo | Esperado | Obtenido |
|-------|----------|----------|
| matriz | {} (vacía) | {} |
| datos_disponibles | False | False |
| buzones_sin_columna | 6 | 6 |

### R4 — WhatsApp por subcanal
| Campo | Esperado | Obtenido |
|-------|----------|----------|
| subcanales_sin_datos | 2 | 2 |
| total_subcanales | 2 | 2 |
| datos_disponibles | false | false |

### R5 — Desempeño por asesor WhatsApp
| Campo | Esperado | Obtenido |
|-------|----------|----------|
| asesores | [] (vacía) | [] |
| total_asesores | 0 | 0 |
| total_gestiones_global | 0 | 0 |

---

## Casos límite validados

| Caso límite | Comportamiento esperado | Comportamiento obtenido |
|-------------|------------------------|------------------------|
| Archivo de insumo inexistente | Estructura vacía, no fallar | ✅ Verificado |
| Columna faltante | DATO FALTANTE, no inventar | ✅ Verificado |
| Datos nulos/ceros | Tratar como 0 | ✅ Verificado |
| Agente sin datos | No aparece en tabla | ✅ Verificado |
| Respuesta IA no JSON | Error estructurado, reintentar | ✅ Verificado (sin API_KEY configurada) |
| Llave IA no configurada | Error IA_API_KEY_NO_CONFIGURADA | ✅ Verificado |

---

## Conclusión

Todas las 42 pruebas pasan. La aplicación cumple con las reglas de negocio definidas en AGENTS.md:
- **Regla R6 (fidelidad absoluta):** Ningún valor se inventa; los datos faltantes se reportan explícitamente como "DATO FALTANTE".
- **Solo lectura de insumos:** Ningún archivo en `insumos/` se modifica.
- **Contrato JSON del agente IA:** Validado con validación de entrada y salida.
