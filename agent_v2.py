from ollama import chat
import subprocess

HOST = "matrix-vps-ai"

TOOLS = {
    "memoria": "free -h",
    "disco": "df -h /",
    "sistema": "hostnamectl",
}

pregunta = input("Pregunta: ").lower()

cmd = None

for palabra, comando in TOOLS.items():
    if palabra in pregunta:
        cmd = comando
        break

if not cmd:
    print("No sé qué comando ejecutar.")
    exit()

ssh_cmd = f'ssh {HOST} "{cmd}"'

resultado = subprocess.run(
    ssh_cmd,
    shell=True,
    capture_output=True,
    text=True
)

prompt = f"""
Actúa como un administrador Linux experto.

Pregunta del usuario:
{pregunta}

Salida:
{resultado.stdout}

Explica el resultado en español.
"""

response = chat(
    model="qwen2.5:7b",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

print("\nRespuesta:\n")
print(response.message.content)