from pathlib import Path
import subprocess
import json
import sys
from config import DEBUG

ROOT = Path(r"C:\infra-lab")
COMMANDS = ROOT / "commands"

CONFIRM_WORDS = {"listo", "continuemos"}

# Colores ANSI para salidas en terminal PowerShell
USER = "\033[96m"      # Cyan
BOT = "\033[92m"       # Verde
SYSTEM = "\033[93m"    # Amarillo
ERROR = "\033[91m"     # Rojo
RESET = "\033[0m"      # Reset


def run_step(step_number, label, args, cwd=None, **kwargs):
    if DEBUG:
        print(f"\n{SYSTEM}{'=' * 60}")
        print(f"  [{step_number}] {label}")
        print(f"{'=' * 60}{RESET}\n")
    else:
        print(f"\n{SYSTEM}{label}{RESET}")

    result = subprocess.run(args, cwd=cwd or ROOT, **kwargs)
    if result.returncode != 0:
        raise Exception(f"{ERROR}{label} falló con código {result.returncode}{RESET}")


def load_pending_evidence():
    pending_file = COMMANDS / "pending_evidence.json"
    if not pending_file.exists():
        return []
    with open(pending_file, "r", encoding="utf-8") as f:
        all_entries = json.load(f)
    return [e for e in all_entries if e.get("status", "pending") == "pending"]


def interactive_privileged_collection(pending_tools):
    """
    Modo interactivo para evidencias privilegiadas con mensajes concisos de alto nivel.
    """
    total = len(pending_tools)

    print(f"\n{SYSTEM}{'=' * 60}")
    print("  Se requiere intervención del operador.")
    print(f"  {total} componente(s) requieren ejecución manual.")
    print(f"{'=' * 60}{RESET}")

    all_collected = True

    for idx, tool in enumerate(pending_tools, start=1):
        name     = tool["name"]
        command  = tool["command"]
        filename = tool["file"]
        category = tool.get("category", "server")
        filepath = ROOT / "evidence" / category / filename

        filepath.parent.mkdir(parents=True, exist_ok=True)

        tmp_name  = f"infra_tmp_{filename}"
        local_path = filepath

        print(f"\n{SYSTEM}[{idx}/{total}] Componente: {name}{RESET}")
        print(f"{SYSTEM}Ejecute el siguiente comando en el servidor:{RESET}\n")
        print(f"  mkdir -p ~/infra_tmp && {command} > ~/infra_tmp/{tmp_name}\n")
        print(f"{SYSTEM}Luego transfiera la evidencia desde esta terminal:{RESET}\n")
        print(f"  scp matrix-vps-ai:~/infra_tmp/{tmp_name} \"{local_path}\"\n")

        while True:
            raw = input(f"{USER}Escribe 'listo' o 'continuemos' para validar: {RESET}").strip().lower()

            if raw not in CONFIRM_WORDS:
                print(f"{ERROR}⚠ Entrada no reconocida. Escribe 'listo' o 'continuemos'.{RESET}\n")
                continue

            if filepath.exists() and filepath.stat().st_size > 0:
                print(f"{BOT}✅ Evidencia validada: {filepath.name}{RESET}\n")
                break
            else:
                print(f"{ERROR}❌ No se encontró el archivo en: {local_path}{RESET}")
                print(f"{ERROR}Asegúrate de haber completado ambos pasos y vuelve a intentarlo.{RESET}\n")

    return all_collected


def run_pipeline(pregunta: str, interactive: bool = False) -> str:
    """
    Ejecuta el pipeline completo de auditoría y soporte para una pregunta dada.
    Retorna el reporte final generado en formato string.
    Funciona como motor agnóstico para Terminal CLI, Interfaz Gradio (app.py) o bot de Matrix/Element.
    """
    question_file = COMMANDS / "question.txt"
    question_file.parent.mkdir(parents=True, exist_ok=True)
    with open(question_file, "w", encoding="utf-8") as f:
        f.write(pregunta)

    # ── PASO 1: Clasificando consulta ────────────────────────────────
    run_step(
        1,
        "1. Clasificando consulta...",
        [sys.executable, "planner.py"],
        input=pregunta,
        text=True
    )

    # ── PASO 2: Recolección de información ───────────────────────────
    run_step(2, "2. Recolección de información...", [sys.executable, "collector.py"])

    # ── PASO 3: Recolección interactiva (si hay pendientes) ──────────
    pending = load_pending_evidence()

    if pending and interactive:
        interactive_privileged_collection(pending)
        run_step(
            3,
            "3. Reconciliando información privilegiada...",
            [sys.executable, "collector.py"]
        )

    # ── PASO 4: Analizando resultados ────────────────────────────────
    run_step(4, "4. Analizando resultados...", [sys.executable, "analyst.py"])

    report_file = ROOT / "reports" / "latest_report.md"
    if report_file.exists():
        return report_file.read_text(encoding="utf-8")
    return "No se pudo generar el reporte."


def launch_web_interface():
    print(f"\n{SYSTEM}Iniciando interfaz web con Gradio (app.py)...{RESET}\n")
    subprocess.run([sys.executable, str(ROOT / "app.py")])


def main():
    if "--web" in sys.argv or "-w" in sys.argv:
        launch_web_interface()
        return

    if DEBUG:
        print(f"{SYSTEM}{'=' * 60}")
        print("  INFRA BOT v2.0  —  Auditoría Asistida (Modo Terminal CLI)")
        print(f"{'=' * 60}{RESET}")

    while True:
        pregunta = input(f"\n{USER}Pregunta (escribe 'salir' o 'web' para interfaz web): {RESET}").strip()
        
        if pregunta.lower() in ["salir", "adios", "exit"]:
            print(f"\n{SYSTEM}Saliendo del asistente...{RESET}")
            break

        if pregunta.lower() in ["web", "gui", "app"]:
            launch_web_interface()
            break

        if not pregunta:
            continue

        reporte = run_pipeline(pregunta, interactive=True)

        if DEBUG:
            print(f"\n{BOT}{'=' * 60}")
            print("  ✅  Pipeline completado correctamente")
            print(f"{'=' * 60}{RESET}")


if __name__ == "__main__":
    main()