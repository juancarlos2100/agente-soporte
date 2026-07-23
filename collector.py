from pathlib import Path
import subprocess
import json
import re
import unicodedata
from tools import TOOLS
from lib.retrieval import tokenize, normalize, STOP_WORDS
from config import DEBUG
from knowledge_synonyms import SYNONYMS

HOST = "matrix-vps-ai"

ROOT = Path(r"C:\infra-lab")

COMMANDS = ROOT / "commands"
COMMANDS.mkdir(
    parents=True,
    exist_ok=True
)
EVIDENCE = ROOT / "evidence" / "server"

EVIDENCE.mkdir(parents=True, exist_ok=True)


def run_remote(cmd):
    return subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", HOST, cmd],
        capture_output=True,
        text=True,
        timeout=15
    )


def expand_query_tokens(query_tokens: list[str]) -> list[str]:
    """
    Expande la lista de tokens usando el diccionario SYNONYMS.
    Ejemplo: 'rfid' -> ['rfid', 'distintivo', 'tid', 'vinculacion', 'vincular', 'escaneo']
    """
    expanded = set(query_tokens)
    for token in query_tokens:
        norm_token = normalize(token)
        for key, syn_list in SYNONYMS.items():
            norm_key = normalize(key)
            norm_syns = [normalize(s) for s in syn_list]
            if norm_token == norm_key or norm_token in norm_syns:
                expanded.add(norm_key)
                for s in norm_syns:
                    expanded.add(s)
    return list(expanded)


def enhanced_knowledge_search(pregunta: str, knowledge_dir: Path, top_n: int = 3) -> list[dict]:
    """
    Motor de búsqueda mejorado en collector.py:
    - Normalización (minúsculas, sin acentos, limpia puntuación)
    - Tokenización y distinción de tokens base vs sinónimos expandidos
    - Coincidencia en TAGS (+3 pts por token base coincidente en TAGS)
    - Coincidencia en SINÓNIMOS (+2 pts por sinónimo coincidente en el bloque)
    - Coincidencia en CONTENIDO (+1 pt por token base coincidente en CONTENIDO)
    - Bonus por coincidencia exacta & en título
    """
    base_tokens = tokenize(pregunta)
    expanded_tokens = expand_query_tokens(base_tokens)

    base_tokens_set = set(base_tokens)
    synonym_tokens_set = set(expanded_tokens) - base_tokens_set

    norm_query = normalize(pregunta)

    if not base_tokens or not knowledge_dir.exists():
        return []

    scored_chunks = []

    for filepath in knowledge_dir.rglob("*"):
        if not filepath.is_file() or filepath.suffix.lower() not in (".md", ".txt"):
            continue

        try:
            raw_text = filepath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        # Separar por encabezados ## (secciones)
        sections = re.split(r"(?=^## )", raw_text, flags=re.MULTILINE)

        for section in sections:
            section = section.strip()
            if not section or len(section) < 30:
                continue

            section_clean = re.sub(r"\n---\s*$", "", section).strip()

            # Extraer título de la sección
            title_match = re.match(r"^##\s+(.+)", section_clean)
            if title_match:
                title = title_match.group(1).strip()
            else:
                first_line = section_clean.split("\n")[0].strip()
                title = re.sub(r"^#+\s*", "", first_line) or filepath.name

            # Extraer TAGS y CONTENIDO
            tags_text = ""
            content_text = section_clean

            if "TAGS:" in section_clean and "CONTENIDO:" in section_clean:
                parts = section_clean.split("CONTENIDO:", 1)
                tags_text = parts[0].replace("TAGS:", "")
                content_text = parts[1]
            elif "TAGS:" in section_clean:
                parts = section_clean.split("TAGS:", 1)
                tags_text = parts[1]

            norm_tags = normalize(tags_text)
            norm_content = normalize(content_text)
            norm_title = normalize(title)

            tags_words = set(norm_tags.split())
            content_words = set(norm_content.split())
            title_words = set(norm_title.split())

            full_chunk_norm = f"{norm_tags} {norm_title} {norm_content}"

            score = 0.0

            # 1. Coincidencia en TAGS (+3 pts por cada token base coincidente en TAGS)
            for token in base_tokens_set:
                if token in tags_words or token in norm_tags:
                    score += 3.0

            # 2. Coincidencia en SINÓNIMOS (+2 pts por cada sinónimo coincidente en el bloque)
            for syn_token in synonym_tokens_set:
                if syn_token in tags_words or syn_token in content_words or syn_token in title_words or syn_token in full_chunk_norm:
                    score += 2.0

            # 3. Coincidencia en CONTENIDO (+1 pt por cada token base coincidente en CONTENIDO)
            for token in base_tokens_set:
                if token in content_words or token in norm_content:
                    score += 1.0

            # Bonus por coincidencia exacta (frase o tags)
            if norm_query and norm_query in norm_content:
                score += 3.0

            if norm_query and norm_query in norm_tags:
                score += 4.0

            # Bonus por título (+1.5 por cada token base coincidente en título)
            for token in base_tokens_set:
                if token in title_words:
                    score += 1.5

            if score > 0:
                scored_chunks.append({
                    "source": filepath.name,
                    "title": title,
                    "score": round(score, 2),
                    "content": section_clean
                })

    # Ordenar por score descendente y seleccionar Top-N
    scored_chunks.sort(key=lambda x: x["score"], reverse=True)
    return scored_chunks[:top_n]


def collect_from_plan():

    plan_file = COMMANDS / "plan.json"

    if not plan_file.exists():
        raise Exception("No existe plan.json")

    with open(plan_file, "r", encoding="utf-8") as f:
        plan = json.load(f)

    evidences = plan.get("evidences", [])

    if DEBUG:
        print("\n=== RECOLECTANDO EVIDENCIA ===\n")

    pending_file = COMMANDS / "pending_command.txt"
    pending_file.write_text(
        "", 
        encoding="utf-8"
    )

    pending_evidence = []

    for evidence in evidences:

        if evidence not in TOOLS:
            if DEBUG:
                print(f"[SKIP] Herramienta desconocida: {evidence}")
            continue

        tool = TOOLS[evidence]
        command = tool["command"]
        filename = tool["file"]
        tool_type = tool.get("type", "automatic")
        category = tool.get("category", "server")
        evidence_dir = ROOT / "evidence" / category
        filepath = evidence_dir / filename

        if tool_type == "knowledge":
            if DEBUG:
                print(f"[INICIO] {evidence} (Búsqueda en Base de Conocimientos)")

            question_file = COMMANDS / "question.txt"
            pregunta = question_file.read_text(encoding="utf-8") if question_file.exists() else ""

            knowledge_dir = ROOT / "knowledge"
            evidence_dir.mkdir(parents=True, exist_ok=True)

            base_tokens = tokenize(pregunta)
            expanded_tokens = expand_query_tokens(base_tokens)

            if DEBUG:
                print(f"  Tokens base: {base_tokens}")
                print(f"  Tokens expandidos: {expanded_tokens}")

            # Ejecutar algoritmo de retrieval mejorado
            results = enhanced_knowledge_search(pregunta, knowledge_dir, top_n=3)

            best_score = results[0]['score'] if results else 0.0
            umbral = 0.25
            confidence = "HIGH" if best_score >= 8.0 else ("LOW" if best_score >= umbral else "NONE")

            if DEBUG:
                print(f"  Best score: {best_score} (Umbral: {umbral}) | Confianza: {confidence}")

                for idx, chunk in enumerate(results, start=1):
                    tag = "PRINCIPAL" if idx == 1 else f"SECUNDARIO {idx - 1}"
                    print(f"  [{chunk['score']} pts] [{tag}] {chunk['source']} -> {chunk['title']}")

            with open(filepath, "w", encoding="utf-8") as f:
                if results and best_score >= umbral:
                    f.write(f"MATCH_CONFIDENCE={confidence}\n\n")
                    for idx, chunk in enumerate(results, start=1):
                        if idx == 1:
                            f.write(f"=== CANDIDATO PRINCIPAL (Fuente: {chunk['source']}, Score: {chunk['score']}) ===\n")
                        else:
                            f.write(f"--- EVIDENCIA SECUNDARIA {idx - 1} (Fuente: {chunk['source']}, Score: {chunk['score']}) ---\n")
                        f.write(chunk["content"])
                        f.write("\n\n")
                else:
                    f.write("NO_MATCH")

            if DEBUG:
                print(f"[FIN] {evidence} — {len(results) if best_score >= umbral else 0} bloque(s) seleccionado(s)")
            continue

        if tool_type == "privileged":

            if filepath.exists() and filepath.stat().st_size > 0:
                # Evidencia ya importada manualmente → reutilizar
                pending_evidence.append({
                    "name": evidence,
                    "command": command,
                    "file": filename,
                    "type": tool_type,
                    "category": category,
                    "status": "collected",
                    "path": str(filepath)
                })
                if DEBUG:
                    print(f"[COLLECTED] {evidence} — evidencia importada encontrada en {filepath}")
            else:
                # Evidencia aún no disponible → marcar como pendiente
                with open(
                    pending_file,
                    "a",
                    encoding="utf-8"
                ) as f:
                    f.write(command + "\n")

                pending_evidence.append({
                    "name": evidence,
                    "command": command,
                    "file": filename,
                    "type": tool_type,
                    "category": category,
                    "status": "pending"
                })
                if DEBUG:
                    print(f"[PRIVILEGED] {evidence} requiere privilegios. Comando agregado a pending_command.txt")

            continue

        # Evidencia automática: si ya fue recolectada y existe en disco, reutilizar
        if filepath.exists() and filepath.stat().st_size > 0:
            if DEBUG:
                print(f"[REUSED] {evidence} — evidencia existente en {filepath}")
            continue

        if DEBUG:
            print(f"[INICIO] {evidence}")

        try:
            result = run_remote(command)
            evidence_dir.mkdir(parents=True, exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(result.stdout)

            if DEBUG:
                print(f"[FIN] {evidence}")

            if result.stderr and DEBUG:
                print("\nSTDERR:")
                print(result.stderr)
        except subprocess.TimeoutExpired:
            if DEBUG:
                print(f"[TIMEOUT] {evidence} — la conexión SSH excedió el tiempo límite (15s)")
        except Exception as e:
            if DEBUG:
                print(f"[ERROR] {evidence} — fallo al recolectar: {e}")

    pending_evidence_file = COMMANDS / "pending_evidence.json"
    with open(pending_evidence_file, "w", encoding="utf-8") as f:
        json.dump(pending_evidence, f, indent=2, ensure_ascii=False)

    if DEBUG:
        print("\n Recolección completada")


if __name__ == "__main__":
    collect_from_plan()