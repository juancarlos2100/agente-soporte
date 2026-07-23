"""
lib/retrieval.py — Motor de búsqueda documental para la Base de Conocimientos.

Pipeline:
  1. Normalización   → minúsculas, elimina acentos, elimina puntuación
  2. Tokenización    → extracción de palabras clave con filtro de stop words
  3. Chunking        → divide cada archivo en bloques lógicos (secciones ##)
  4. Ranking         → intersección de tokens query vs chunk (Jaccard-like)
  5. Selección Top-N → devuelve los N bloques más relevantes
"""

import re
import math
import unicodedata
from pathlib import Path


# ─────────────────────────────────────────────────────────────
#  STOP WORDS — Español (palabras funcionales sin valor semántico)
# ─────────────────────────────────────────────────────────────

STOP_WORDS = {
    # Artículos y determinantes
    "el", "la", "los", "las", "un", "una", "unos", "unas",
    # Preposiciones
    "de", "del", "en", "con", "por", "para", "sin", "sobre",
    "entre", "hacia", "desde", "hasta", "ante", "bajo",
    # Conjunciones
    "y", "o", "ni", "que", "pero", "sino", "como", "porque",
    # Pronombres y demostrativos
    "yo", "tu", "el", "ella", "nos", "este", "esta", "esto",
    "ese", "esa", "eso", "aquel", "aquella", "aquello",
    "cual", "cuales", "quien",
    # Verbos auxiliares y comunes genéricos
    "es", "son", "ser", "fue", "hay", "estar",
    "tiene", "puede", "debe", "debo", "hacer",
    "hago", "tengo", "puedo", "quiero", "necesito", "saber",
    "decir", "dice", "haz", "ver",
    # Adverbios genéricos
    "no", "si", "ya", "muy", "mas", "menos",
    "bien", "mal", "solo", "donde", "cuando",
    # Cuantificadores
    "todo", "toda", "todos", "todas", "cada", "otro", "otra",
    "otros", "otras", "algo", "nada", "mucho", "poco",
    # Interrogativos genéricos
    "favor", "ayuda", "caso",
}


# ─────────────────────────────────────────────────────────────
#  1. NORMALIZACIÓN
# ─────────────────────────────────────────────────────────────

def normalize(text: str) -> str:
    """
    Normaliza texto:
      - Convierte a minúsculas
      - Elimina acentos (NFD + filtro de marcas diacríticas)
      - Elimina puntuación y caracteres especiales
    """
    text = text.lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ─────────────────────────────────────────────────────────────
#  2. TOKENIZACIÓN
# ─────────────────────────────────────────────────────────────

def tokenize(text: str, min_length: int = 3) -> list[str]:
    """
    Extrae tokens únicos significativos:
      - Filtra stop words
      - Longitud mínima configurable
      - Preserva orden, elimina duplicados
    """
    normalized = normalize(text)
    words = normalized.split()
    seen = set()
    tokens = []
    for w in words:
        if len(w) >= min_length and w not in STOP_WORDS and w not in seen:
            seen.add(w)
            tokens.append(w)
    return tokens


# ─────────────────────────────────────────────────────────────
#  3. CHUNKING — Divide archivos en bloques lógicos
# ─────────────────────────────────────────────────────────────

def chunk_document(filename: str, content: str) -> list[dict]:
    """
    Divide un documento en bloques lógicos usando encabezados
    Markdown (## ) como separadores de sección.

    Retorna lista de dicts:
      [{"source": str, "title": str, "content": str}, ...]
    """
    # Separar por encabezados ## (nivel 2)
    # El patrón captura la línea del encabezado como inicio de cada bloque
    sections = re.split(r"(?=^## )", content, flags=re.MULTILINE)

    chunks = []
    for section in sections:
        section = section.strip()
        if not section:
            continue

        # Limpiar separadores --- del final del bloque
        section = re.sub(r"\n---\s*$", "", section).strip()

        # Extraer título si empieza con ##
        title_match = re.match(r"^##\s+(.+)", section)
        if title_match:
            title = title_match.group(1).strip()
        else:
            # Bloque sin encabezado (ej. cabecera del archivo con # título)
            first_line = section.split("\n")[0].strip()
            title = re.sub(r"^#+\s*", "", first_line) or filename

        # Ignorar bloques muy cortos (tablas sueltas, líneas vacías)
        if len(section) < 30:
            continue

        chunks.append({
            "source": filename,
            "title": title,
            "content": section,
        })

    # Si no se pudo dividir (archivo sin ##), tratar como bloque único
    if not chunks and len(content.strip()) >= 30:
        chunks.append({
            "source": filename,
            "title": filename,
            "content": content.strip(),
        })

    return chunks


# ─────────────────────────────────────────────────────────────
#  4. RANKING — Intersección de tokens (Jaccard-like + TF bonus)
# ─────────────────────────────────────────────────────────────

def score_chunk(query_tokens: list[str], chunk: dict) -> float:
    """
    Puntúa un bloque mediante intersección de tokens:
      1. Tokeniza el contenido del bloque (incluyendo título y nombre de archivo)
      2. Calcula tokens en común con la query
      3. Score = |intersección| / |query_tokens| + bonus TF + bonus TAGS

    Esto favorece bloques donde aparecen MÚLTIPLES palabras
    de la pregunta, no solo una palabra genérica.
    """
    source_name = chunk.get("source", "")
    content_raw = chunk.get("content", "")

    tags_text = ""
    if "TAGS:" in content_raw and "CONTENIDO:" in content_raw:
        parts = content_raw.split("CONTENIDO:", 1)
        tags_text = parts[0].replace("TAGS:", "")
        content_raw = parts[1]

    full_chunk_text = f"{source_name} {chunk.get('title', '')}\n{tags_text}\n{content_raw}"
    
    chunk_tokens = set(tokenize(full_chunk_text, min_length=3))
    tags_tokens = set(tokenize(tags_text, min_length=3))
    query_set = set(query_tokens)

    if not query_set:
        return 0.0

    # Intersección: tokens de la query que aparecen en el chunk
    common = query_set & chunk_tokens
    if not common:
        return 0.0

    # Score base: proporción de tokens de la query encontrados
    intersection_score = len(common) / len(query_set)

    # Bonus TAGS: Si el token está en los tags, se bonifica fuertemente (+0.5 por cada tag hit)
    tags_bonus = sum(0.5 for token in common if token in tags_tokens)

    # Bonus TF: frecuencia de aparición de los tokens comunes en todo el chunk
    chunk_normalized = normalize(full_chunk_text)
    tf_bonus = 0.0
    for token in common:
        count = chunk_normalized.count(token)
        if count > 1:
            tf_bonus += math.log(count, 2)

    score = intersection_score + tags_bonus + (tf_bonus * 0.1)

    return round(score, 3)


# ─────────────────────────────────────────────────────────────
#  5. SELECCIÓN TOP-N — Pipeline completo
# ─────────────────────────────────────────────────────────────

def search_knowledge(
    query: str,
    knowledge_dir: Path,
    top_n: int = 3,
    extensions: tuple = (".md", ".txt"),
) -> list[dict]:
    """
    Pipeline completo de búsqueda por bloques:
      1. Tokeniza la query
      2. Escanea archivos en knowledge_dir
      3. Divide cada archivo en chunks (secciones ##)
      4. Puntúa cada chunk por intersección de tokens
      5. Retorna los top_n chunks más relevantes

    Retorna lista de dicts:
      [{"source": str, "title": str, "score": float, "content": str}, ...]
    """
    query_tokens = tokenize(query)

    if not query_tokens:
        return []

    if not knowledge_dir.exists():
        return []

    all_chunks = []

    # Escanear y dividir en chunks
    for filepath in knowledge_dir.rglob("*"):
        if not filepath.is_file():
            continue
        if filepath.suffix.lower() not in extensions:
            continue

        try:
            content = filepath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        chunks = chunk_document(filepath.name, content)
        all_chunks.extend(chunks)

    # Puntuar cada chunk
    scored = []
    for chunk in all_chunks:
        score = score_chunk(query_tokens, chunk)
        if score > 0:
            scored.append({
                "source": chunk["source"],
                "title": chunk["title"],
                "score": score,
                "content": chunk["content"],
            })

    # Ordenar por score descendente y seleccionar Top-N
    scored.sort(key=lambda d: d["score"], reverse=True)

    return scored[:top_n]
