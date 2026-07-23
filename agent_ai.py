import subprocess
from ollama import chat

HOST = "matrix-vps-ai"

def run_remote(cmd):
    ssh_cmd = f'ssh {HOST} "{cmd}"'

    result = subprocess.run(
        ssh_cmd,
        shell=True,
        capture_output=True,
        text=True,
        timeout=30
    )

    return result.stdout, result.stderr

print("=" * 60)
print("INFRA BOT AI v0.1")
print("=" * 60)

stdout, stderr = run_remote("free -h")

if stderr:
    print("ERROR DETECTADO:")
    print(stderr)
    exit()

prompt = f"""
Actúa como un administrador Linux y DevOps experto.

Analiza la siguiente salida del comando 'free -h'
y genera un diagnóstico breve y profesional.

Salida:

{stdout}
"""

response = chat(
    model='qwen2.5:7b',
    messages=[
        {
            'role': 'user',
            'content': prompt
        }
    ]
)

print("\nDIAGNÓSTICO:\n")
print(response.message.content)
