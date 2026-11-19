# AGENTS.md

## Qué es esta app

Aplicación web de análisis operativo de servicio al cliente para un Contact Center bancario. Lee los cierres mensuales de los canales de atención (Chatbot/CORI, Llamadas y Correos, WhatsApp/Redes Sociales) desde archivos Excel de insumos, aplica reglas de negocio estrictas y genera un informe ejecutivo en formato Markdown listo para presentar a la alta dirección. Incluye una integración opcional con un agente de IA que estructura el informe a partir de un contrato JSON.

---

## Datos de entrada

Los archivos de entrada residen exclusivamente en la carpeta `insumos/` (solo lectura, nunca se modifican). Hay 3 archivos Excel:

### 1. `Control CHATBOT.xlsx` (canal: Chatbot / CORI)

Hojas detectadas:
- **Intervalos CORI**: Mes, Respuesta Dialog Flow, y totales por intervalo.
- **Chat**: Nivel, N1, Agente, Contestadas, Antes del umbral, Abandonadas, AHT, Ofrecidas, %TR, %NS, Tiempo de ocupación. Datos por agente (aprox. 50 filas).
- **Vínculos**: Mapeo de códigos de canal a nivel (ej. `WC_NBCR_BCR` → N1, `WC_NBCR_BCR_OPC` → OPC, `WC_NBCR_BCR_Tucan` → Tucan).

### 2. `Control llamadas y correos.xlsx` (canales: Llamadas y Correos)

Hojas detectadas:
- **Control Mensual**, **Control Diario**, **Control Intervalo**, **Control Auxiliares**, **Control Agentes**, **%Ocupación por intervalo**, **Vínculos**.
- Columnas principales observadas en Vínculos: Application, AgentLogin, Nombre, Nivel, Entrantes, Contestadas, Abandonadas, Cont. Antes 20 seg., Cont. Desp 20 seg, Aban. Antes 20 seg., Aban. Desp 20 seg, Tiempo Conversación, AHT, % Service Level, Tasa de Respuesta, Llamadas Salientes, Correos, Correos Empresas, Contracargos, y muchas más de trazabilidad de interacciones.
- En Control Agentes se observan: Nombre de Agente, Llamadas Contestadas, Llamadas Salientes, Correos, AHT, % Ocupación, Nivel.

### 3. `Control WhatsApp.xlsx` (canal: WhatsApp / Redes Sociales)

Hojas detectadas:
- **Control Agentes**: Nivel, Redes, AgentLogin, Nombre, Entrantes, Contestadas, Abandonadas, AHT, Tasa de Respuesta, Tiempo Conversación, % Service Level, Llamadas Salientes, Correos.
- **Whatsapp**: mes, Status, campaign, Grupo, category.
- **Diario agentes(REDES)**: días de la semana con Promedio > 60 Interacciones y Agentes > 60 interacciones.
- **Vínculos**: mismas columnas de trazabilidad que el archivo de llamadas y correos (35,371 filas).

**Buzones de correos confirmados en los insumos:** Bienes adquiridos, Centro Asistencia N1, Centro Asistencia N2, Operativa CAC PCI, Servicio oficina virtual, Soporte CAC (según el contexto y la columna Nivel con valores N1, N2, PCI, Redes).

---

## Reglas de negocio (código, sin IA)

Todas las reglas se implementan como funciones puras en Python, sin llamar a ningún modelo de IA. Una función por regla, con su comentario.

### R1 — Métricas globales por canal
Entrada: datos crudos de los 3 archivos Excel.
Salida: tabla con 4 filas (canales: Chatbot/CORI, Llamadas, Correos, WhatsApp/Redes Sociales) y columnas: Cantidad Atendida, AHT, TR, Gestiones por Asesor.
Código: leer cada insumo, filtrar por canal, sumar contestadas/atendidas, calcular AHT promedio, calcular TR (Tasa de Respuesta), contar gestiones por asesor.
Regla: si un canal no tiene datos en los insumos, reportar "dato faltante" sin inventar valor.

### R2 — Desglose de correos por buzón
Entrada: hoja de correos del insumo `Control llamadas y correos.xlsx`.
Salida: tabla con 6 filas (buzones: Bienes adquiridos, Centro Asistencia N1, Centro Asistencia N2, Operativa CAC PCI, Servicio oficina virtual, Soporte CAC) y columna: Cantidad atendida.
Código: agrupar por buzón, sumar cantidad atendida.
Regla: si falta algún buzón, reportarlo explícitamente.

### R3 — Matriz Asesor vs. Buzón (correos)
Entrada: datos de correos con asesor y buzón.
Salida: tabla cruzada donde filas son asesores y columnas son los 6 buzones, celdas con cantidad de correos gestionados.
Código: pivotar datos de asesor × buzón.
Regla: celdas vacías = 0 gestiones, no se inventa.

### R4 — Desglose de WhatsApp por subcanal
Entrada: datos de `Control WhatsApp.xlsx`.
Salida: 2 subcanales por separado (WhatsApp y Llamadas), cada uno con: Atendidas, AHT, TR.
Código: separar por tipo de contacto, calcular métricas.
Regla: si falta AHT o TR en algún subcanal, reportar dato faltante.

### R5 — Desempeño por asesor (WhatsApp / Redes Sociales)
Entrada: datos por asesor del insumo de WhatsApp.
Salida: tabla por asesor con: Cantidad atendida en WhatsApp, Cantidad de llamadas atendidas, Tiempo de ocupación, AHT del asesor, Total de gestiones atendidas.
Código: agrupar por asesor, sumar cada métrica.
Regla: asesor sin datos = no aparece en la tabla, no se inventa fila.

### R6 — Fidelidad absoluta y prohibición de invención
Código: antes de devolver cualquier número, verificar que existe en el insumo origen. Si no existe, lanzar error o devolver "DATO FALTANTE" en lugar de estimar.

---

## Lo que hace el agente de IA (con el contrato JSON)

El agente de IA **no calcula métricas** (eso lo hace el código R1-R6). El agente recibe los datos ya procesados y devuelve el informe estructurado en formato Markdown.

### Contrato JSON de entrada

```json
{
  "canales": [
    {
      "nombre": "Chatbot/CORI",
      "cantidad_atendida": 0,
      "aht": 0,
      "tr": 0,
      "gestiones_asesor": []
    },
    {
      "nombre": "Llamadas",
      "cantidad_atendida": 0,
      "aht": 0,
      "tr": 0,
      "gestiones_asesor": []
    },
    {
      "nombre": "Correos",
      "cantidad_atendida": 0,
      "aht": 0,
      "tr": 0,
      "gestiones_asesor": []
    },
    {
      "nombre": "WhatsApp/Redes Sociales",
      "cantidad_atendida": 0,
      "aht": 0,
      "tr": 0,
      "gestiones_asesor": []
    }
  ],
  "correos_por_buzon": [
    { "buzon": "Bienes adquiridos", "cantidad": 0 },
    { "buzon": "Centro Asistencia N1", "cantidad": 0 },
    { "buzon": "Centro Asistencia N2", "cantidad": 0 },
    { "buzon": "Operativa CAC PCI", "cantidad": 0 },
    { "buzon": "Servicio oficina virtual", "cantidad": 0 },
    { "buzon": "Soporte CAC", "cantidad": 0 }
  ],
  "matriz_asesor_buzon": [
    { "asesor": "string", "buzones": { "Bienes adquiridos": 0, ... } }
  ],
  "whatsapp_subcanales": [
    { "subcanal": "WhatsApp", "atendidas": 0, "aht": 0, "tr": 0 },
    { "subcanal": "Llamadas", "atendidas": 0, "aht": 0, "tr": 0 }
  ],
  "whatsapp_asesores": [
    { "asesor": "string", "whatsapp": 0, "llamadas": 0, "tiempo_ocupacion": "string", "aht": 0, "total": 0 }
  ],
  "datos_faltantes": ["lista de campos que no se encontraron en los insumos"]
}
```

### Contrato JSON de salida

```json
{
  "informe_markdown": "string",
  "secciones": ["Resumen Operativo General", "Desglose de Correos", "Desglose de WhatsApp", "Desglose por Asesor"],
  "observaciones": ["notas sobre datos faltantes o anomalías"]
}
```

### Integración
- La llave de IA se lee desde `.env` (variable: `IA_API_KEY`).
- Nunca se hardcodea la llave en el código.
- Si el agente no devuelve JSON válido, la app muestra error y no inventa contenido.

---

## Qué produce la app

- Informe ejecutivo en formato **Markdown** (según respuesta 5).
- Tabla comparativa global por canal (Cantidad Atendida, AHT, TR, Gestiones por Asesor).
- Tabla de correos por buzón (6 buzones).
- Matriz Asesor vs. Buzón.
- Indicadores de WhatsApp por subcanal (Atendidas, AHT, TR).
- Tabla de desempeño por asesor de WhatsApp.
- Nota explícita de cualquier dato faltante.
- Pantalla web con contadores grandes y tablas con filtro (frontend).

---

## Quién decide

- **El código (reglas R1-R6)** decide los cálculos y valida que los datos existan en los insumos.
- **El agente de IA** decide la redacción y estructura del informe Markdown, pero solo con los datos que el código le entrega.
- **El usuario/supervisor** decide si falta un dato: si el código reporta "DATO FALTANTE", se detiene y pregunta antes de continuar (regla del contexto: "si falta un dato, pregunte").
- **El revisor** valida que nada esté inventado y que todo esté en `AGENTS.md`.

---

## Cifras de control

(Se completa con los valores esperados una vez @tester ejecute las pruebas contra los insumos reales. Ejemplos de lo que se controlará: cantidad atendida por canal, AHT promedio, TR por canal, total de gestiones por asesor, suma de buzones = total de correos.)

---

## Casos límite

1. **Archivo de insumo vacío o sin hojas**: la app reporta error y no inventa estructura.
2. **Columna faltante** (ej. no existe "AHT" en una hoja): reportar "DATO FALTANTE" para esa métrica.
3. **Datos nulos o ceros**: tratar como 0 gestiones, no omitir silenciosamente.
4. **Agente sin datos**: no aparece en las tablas de asesor.
5. **Buzón de correos no encontrado en insumos**: reportar explícitamente cuál falta.
6. **Respuesta del agente de IA que no es JSON**: reintentar una vez; si falla, mostrar error estructurado.
7. **Límite de llave gratuita de IA alcanzado**: app avisa y continúa con el informe generado por código (sin IA).

---

## Reglas del sistema

1. **No modificar `insumos/` ni `contexto/`** bajo ninguna circunstancia (solo lectura).
2. **No inventar columnas, archivos ni reglas** que no estén en `AGENTS.md` ni en el contexto.
3. **Si falta un dato, preguntar antes de asumir** (regla del contexto).
4. **No hardcodear llaves API**; leer solo de `.env`.
5. **Responder en español** (tono profesional, fácil de leer).
6. **Todo salida cuantitativa en tablas Markdown**; hallazgos en viñetas.
7. **El agente de IA nunca calcula métricas**; solo redacta el informe con datos ya validados por código.
8. **Cualquier contradicción entre contexto e insumos se reporta al usuario** antes de continuar.

---

> La variable de entorno para la llave de IA es `IA_API_KEY` (definida en `.env`). El proveedor de IA aún no se ha especificado; se definirá al momento de implementar la integración.
