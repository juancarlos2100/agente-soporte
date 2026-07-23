from pathlib import Path
from ollama import chat
import json
import re
import sys
import unicodedata

from tools import TOOLS
from config import DEBUG

ROOT = Path(r"C:\infra-lab")
COMMANDS = ROOT / "commands"

COMMANDS.mkdir(parents=True, exist_ok=True)

if sys.stdin.isatty():
    pregunta = input("Pregunta: ")
else:
    pregunta = sys.stdin.read().strip()

if not pregunta:
    raise Exception("No se recibió ninguna pregunta")

question_file = COMMANDS / "question.txt"
question_file.write_text(pregunta, encoding="utf-8")


def extract_json(text):
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        raise Exception(f"No se encontró JSON válido en la respuesta: {text}")
    return json.loads(match.group())


def normalize_text(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text


SUPPORT_KEYWORDS = [
    "licencia", "rfid", "casco", "holograma", "ciudadano",
    "aplicacion", "aplicación", "validacion", "validación",
    "error", "tramite", "trámite", "distintivo", "carta",
    "consentimiento", "extranjera", "nacionalidad", "pm95",
    "pm85", "rf88", "standby", "escaneo", "vinculacion", "vinculación",
    "instalar", "instalación", "instalacion"
]

norm_pregunta = normalize_text(pregunta)
is_support_deterministic = any(normalize_text(kw) in norm_pregunta for kw in SUPPORT_KEYWORDS)

if is_support_deterministic:
    intent = "support"
    if DEBUG:
        print("\n[CLASIFICADOR DETERMINÍSTICO] Coincidencia con palabra clave de soporte detectada -> intent = 'support'")
        print("[PASO B] Intent 'support' detectado -> Plan fijo asignado: ['knowledge_search']")
    plan = {
        "intent": intent,
        "evidences": ["knowledge_search"]
    }
else:
    # ─────────────────────────────────────────────────────────────────
    # PASO A: Clasificación de Intención (Primera llamada LLM)
    # ─────────────────────────────────────────────────────────────────
    prompt_intent = f"""
Eres un clasificador experto de intenciones para un sistema de auditoría y soporte.

El usuario preguntó:
"{pregunta}"

Clasifica la pregunta en exactamente una de las siguientes intenciones:

1. "support": Preguntas sobre soporte funcional, procedimientos, errores de aplicación, licencias, validador, RFID, distintivo, casco, holograma, trámites, carta consentimiento, nacionalidad extranjera, conexión inestable, internet, PM95, PM85, RF88, standby, escaneo, vinculación.
NOTA IMPORTANTE: Si la pregunta se refiere a trámites, licencias, validador, RFID o soporte de aplicación SIN mencionar servidores, Kubernetes, pods, CPU, RAM, disco, Matrix o Synapse, ES OBLIGATORIAMENTE "support".

2. "infra": Preguntas técnicas sobre servidores, servicios, Kubernetes, pods, helm, CPU, RAM, memoria, disco, procesos, Matrix, Synapse, TLS, rendimiento o recursos del sistema.

3. "mixed": Preguntas que combinan EXPLÍCITAMENTE aspectos de infraestructura (servidores, pods, RAM, disco, Matrix) Y aspectos de soporte funcional/trámites en la misma consulta.

Responde ÚNICAMENTE con un JSON válido en este formato exacto:
{{
  "intent": "support"
}}

No escribas explicaciones.
No uses markdown.
Solo JSON puro.
"""

    response_intent = chat(
        model="qwen2.5:7b",
        messages=[{"role": "user", "content": prompt_intent}]
    )

    intent_data = extract_json(response_intent.message.content.strip())
    intent = intent_data.get("intent", "support").lower()

    if intent not in ["support", "infra", "mixed"]:
        intent = "support"

    if DEBUG:
        print(f"\n[PASO A] Intención clasificada por LLM: {intent}")

    # ─────────────────────────────────────────────────────────────────
    # PASO B: Determinación del Plan según el Intent
    # ─────────────────────────────────────────────────────────────────
    if intent == "support":
        if DEBUG:
            print("[PASO B] Intent 'support' detectado -> Plan fijo asignado: ['knowledge_search']")
        plan = {
            "intent": intent,
            "evidences": ["knowledge_search"]
        }
    else:
        if DEBUG:
            print(f"[PASO B] Intent '{intent}' detectado -> Realizando llamada LLM para selección de evidencias...")

        catalogo = []
        for nombre, tool in TOOLS.items():
            if intent == "infra" and nombre == "knowledge_search":
                continue
            descripcion = tool.get("description", "Sin descripción")
            tool_type = tool.get("type", "automatic")
            catalogo.append(f"- {nombre}: {descripcion} ({tool_type})")

        catalogo_texto = "\n".join(catalogo)

        prompt_evidence = f"""
Eres un selector de herramientas de evidencias para diagnóstico de infraestructura.

El usuario preguntó:
"{pregunta}"

Catálogo de herramientas disponibles:
{catalogo_texto}

Selecciona únicamente las herramientas del catálogo necesarias para responder a la pregunta.

Responde ÚNICAMENTE un objeto JSON válido con el formato:
{{
  "evidences": [
    "nombre_herramienta"
  ]
}}

No escribas explicaciones.
No uses markdown.
Solo JSON puro.
"""

        response_evidence = chat(
            model="qwen2.5:7b",
            messages=[{"role": "user", "content": prompt_evidence}]
        )

        evidence_data = extract_json(response_evidence.message.content.strip())
        evidences = evidence_data.get("evidences", [])

        # Filtrar solo herramientas válidas existentes en TOOLS
        evidences = [ev for ev in evidences if ev in TOOLS]

        if intent == "mixed" and "knowledge_search" not in evidences:
            evidences.append("knowledge_search")

        # Si no se seleccionó ninguna evidencia por error, fallback seguro
        if not evidences:
            evidences = ["memory", "disk"] if intent == "infra" else ["knowledge_search"]

        plan = {
            "intent": intent,
            "evidences": evidences
        }

if DEBUG:
    print("\nPlan generado:\n")
    print(json.dumps(plan, indent=2))

plan_file = COMMANDS / "plan.json"

with open(plan_file, "w", encoding="utf-8") as f:
    json.dump(plan, f, indent=2)

if DEBUG:
    print(f"\nPlan guardado en:")
    print(plan_file)
