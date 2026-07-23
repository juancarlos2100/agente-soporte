from pathlib import Path
from ollama import chat
import json
from tools import TOOLS
from config import DEBUG

ROOT = Path(r"C:\infra-lab")

COMMANDS = ROOT / "commands"
REPORTS = ROOT / "reports"

REPORTS.mkdir(parents=True, exist_ok=True)

if DEBUG:
    print("=" * 60)
    print("INFRA BOT ANALYST")
    print("=" * 60)

plan_file = COMMANDS / "plan.json"

if not plan_file.exists():
    raise Exception("No existe plan.json")

if DEBUG:
    print("\n[1] Leyendo plan...")

with open(plan_file, "r", encoding="utf-8") as f:
    plan = json.load(f)

evidences = plan.get("evidences", [])

if DEBUG:
    print(f"[OK] Evidencias solicitadas: {evidences}")
    print("\n[2] Cargando evidencias...")

is_knowledge = any(TOOLS[e].get("type") == "knowledge" for e in evidences if e in TOOLS)

if is_knowledge and DEBUG:
    print("[MODO SOPORTE] Detectado modo conocimiento -> Se cargará únicamente 'knowledge_results.txt' omitiendo evidencias de infraestructura.")

contexto = ""
no_match_detected = False

match_confidence = "UNKNOWN"

for evidence in evidences:

    if evidence not in TOOLS:
        if DEBUG:
            print(f"[SKIP] Herramienta desconocida: {evidence}")
        continue

    tool = TOOLS[evidence]

    filename = tool["file"]
    category = tool.get("category", "server")
    tool_type = tool.get("type", "automatic")

    # Si es modo conocimiento (soporte), filtrar evidencias de infraestructura
    if is_knowledge and tool_type != "knowledge":
        if DEBUG:
            print(f"[SKIP MODO SOPORTE] Omitiendo evidencia irrelevante: {evidence} ({filename})")
        continue

    evidence_dir = ROOT / "evidence" / category
    filepath = evidence_dir / filename

    if not filepath.exists():
        if tool_type == "privileged":
            if DEBUG:
                print(f"[PENDING] {evidence} es privilegiada y sin evidencia importada")
        else:
            if DEBUG:
                print(f"[ERROR] No existe evidencia: {filepath}")
        continue

    contenido = filepath.read_text(encoding="utf-8")
    if filename == "knowledge_results.txt":
        if contenido.strip() == "NO_MATCH":
            no_match_detected = True
        elif "MATCH_CONFIDENCE=HIGH" in contenido:
            match_confidence = "HIGH"
        elif "MATCH_CONFIDENCE=LOW" in contenido:
            match_confidence = "LOW"

    contexto += f"\n\n===== {evidence} ({category}) =====\n"
    contexto += contenido

    if DEBUG:
        if tool_type == "privileged":
            print(f"[COLLECTED] {evidence} — evidencia privilegiada importada")
        else:
            print(f"[OK] {filename}")

if DEBUG:
    print("\n[2b] Revisando estado de evidencias privilegiadas...")

pending_evidence_file = COMMANDS / "pending_evidence.json"
pending_tools = []

if pending_evidence_file.exists():
    with open(pending_evidence_file, "r", encoding="utf-8") as f:
        all_privileged = json.load(f)

    # Solo los que siguen pendientes (no tienen evidencia importada)
    pending_tools = [
        pt for pt in all_privileged
        if pt.get("status", "pending") == "pending"
    ]

    collected_count = len(all_privileged) - len(pending_tools)
    if DEBUG:
        print(f"[OK] Privilegiadas recopiladas: {collected_count} | Pendientes: {len(pending_tools)}")
else:
    if DEBUG:
        print("[INFO] No existe pending_evidence.json, se asume sin pendientes")

contexto_pendiente = ""

if pending_tools:
    contexto_pendiente += "\n\n===== COMPONENTES PENDIENTES (sin evidencia disponible) =====\n"
    contexto_pendiente += "Los siguientes componentes requieren privilegios y AÚN NO han sido recolectados.\n"
    contexto_pendiente += "NO debes emitir conclusiones ni hallazgos sobre ellos.\n\n"
    for pt in pending_tools:
        contexto_pendiente += (
            f"  - Nombre   : {pt['name']}\n"
            f"    Categoría: {pt.get('category', 'server')}\n"
            f"    Archivo   : {pt['file']}\n"
            f"    Comando   : {pt['command']}\n\n"
        )

auditoria_parcial = bool(pending_tools)

cabecera_auditoria = (
    "ESTA ES UNA AUDITORÍA PARCIAL. Los componentes pendientes están listados abajo.\n"
    "No emitas ningún hallazgo, riesgo ni recomendación sobre ellos basándote en suposiciones."
    if auditoria_parcial else
    "Esta es una auditoría COMPLETA. Toda la evidencia solicitada está disponible."
)

seccion_6 = (
    "## 6. EVIDENCIA FALTANTE Y LIMITACIONES\n"
    "Explica qué componentes están pendientes, por qué su ausencia limita las conclusiones "
    "y qué decisiones no pueden tomarse hasta que esa evidencia esté disponible."
    if auditoria_parcial else
    "## 6. CONCLUSIÓN\n"
    "Resume el estado general de la infraestructura con base en toda la evidencia disponible."
)

estado_auditoria = (
    "**⚠ Auditoría PARCIAL** — existen componentes sin evidencia."
    if auditoria_parcial else
    "** Auditoría COMPLETA** — toda la evidencia solicitada fue evaluada."
)

if DEBUG:
    print("\n[3] Analizando con Qwen...")

if is_knowledge:
    question_file = COMMANDS / "question.txt"
    pregunta = question_file.read_text(encoding="utf-8").strip() if question_file.exists() else "Pregunta desconocida"
    
    if no_match_detected or not contexto.strip() or "NO_MATCH" in contexto:
        prompt = None
        reporte = "No existe documentación suficiente para responder esta consulta. Escalar a soporte humano."
    else:
        prompt = f"""
Eres un especialista de soporte técnico experto. Tu objetivo es responder la consulta del usuario de forma directa, técnica, profesional y natural.

Pregunta del usuario:
{pregunta}

--- INFORMACIÓN TÉCNICA DE SOPORTE ---
{contexto}
--- FIN DE INFORMACIÓN ---

INSTRUCCIONES Y REGLAS DE RESPUESTA:
1. Responde de manera natural, técnica y fluida, directo a la solución o explicación de la duda del usuario.
2. REGLA ABSOLUTA: NUNCA menciones ni incluyas metadatos internos, etiquetas de búsqueda o muletillas de documentación. Está PROHIBIDO usar frases o palabras como:
   - "CANDIDATO PRINCIPAL" o "EVIDENCIA SECUNDARIA"
   - "puntaje de confianza", "Score", "MATCH_CONFIDENCE", "Fuente:"
   - "En base a la información proporcionada...", "El documento menciona...", "Según la documentación..."
3. Explica claramente la causa, diagnóstico, pasos de solución o valores de configuración (indicando valores por defecto y procedimientos de ajuste recomendados si aplica).
4. Mantén un tono técnico pero cercano y natural en español, estructurando el contenido en párrafos claros o viñetas según convenga.
"""
else:
    prompt = f"""
Eres un auditor de infraestructura técnica senior. Tu tarea es producir un informe de auditoría
basado EXCLUSIVAMENTE en la interpretación técnica del contenido de las evidencias recolectadas.

REGLAS ABSOLUTAS:
- NUNCA menciones nombres de archivos como hallazgos (prohibido: "el archivo X contiene...", "matrix_health.txt indica...").
- Interpreta el CONTENIDO de cada evidencia como un auditor, no como un inventario de archivos.
- Ejemplos de interpretación correcta:
    * HTTP 200 en /health → el servicio está respondiendo y disponible
    * Respuesta válida de /_matrix/client/versions con lista de versiones → Synapse operativo, versión del protocolo Matrix identificada
    * Certificado TLS emitido por Let's Encrypt con fecha de expiración futura → TLS válido, CA pública confiable
    * Proceso con alto consumo de CPU visible en top → posible problema de rendimiento en [proceso]
    * Campo "server" en cabecera HTTP → versión del servidor expuesta, riesgo de fingerprinting
- NO inventes ni asumas el estado de ningún componente que no tenga evidencia en este contexto.
- Si una conclusión requiere evidencia que está pendiente, márcala explícitamente como "⚠ No evaluable: falta evidencia de [componente]".

{cabecera_auditoria}

--- EVIDENCIA RECOLECTADA ---
{contexto if contexto.strip() else '(ninguna evidencia disponible aún)'}

{contexto_pendiente}

Genera el reporte con las siguientes secciones en Markdown:

## 1. ESTADO DE LA AUDITORÍA
{estado_auditoria}
Tabla con dos columnas: Componente | Estado (Evaluado / Pendiente - requiere privilegios).

## 2. RESUMEN EJECUTIVO
2-4 párrafos. Describe el estado real de la infraestructura basándote en los datos interpretados.
No menciones archivos. Habla de servicios, protocolos, rendimiento, seguridad.

## 3. HALLAZGOS TÉCNICOS
Lista de hallazgos concretos. Cada hallazgo debe:
- Describir qué se observó en el contenido (no el nombre del archivo)
- Clasificarse como: ✅ Correcto | ⚠ Advertencia | 🔴 Crítico
- Explicar la implicación técnica del hallazgo

## 4. RIESGOS IDENTIFICADOS
Solo sobre componentes con evidencia. Para los pendientes: "⚠ No evaluable: falta evidencia de [componente] — [qué riesgo podría existir pero no se puede confirmar]".

## 5. RECOMENDACIONES
Acciones concretas y priorizadas. Para componentes pendientes: indica que deben recolectarse antes de concluir la auditoría.

{seccion_6}
"""

if no_match_detected or prompt is None:
    reporte = "No existe documentación suficiente para responder esta consulta. Escalar a soporte humano."
else:
    response = chat(
        model="qwen2.5:7b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    reporte = response.message.content

report_file = REPORTS / "latest_report.md"

report_file.write_text(
    reporte,
    encoding="utf-8"
)

# Imprimir únicamente la respuesta limpia en verde BOT
print(f"\033[92m{reporte}\033[0m")

if DEBUG:
    print(f"\n Reporte guardado en: {report_file}")
