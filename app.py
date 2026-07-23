from pathlib import Path
import gradio as gr
from agent import run_pipeline, ROOT, COMMANDS

custom_css = """
body, .gradio-container {
    background-color: #111827 !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
    color: #e5e7eb !important;
}

.header-container {
    text-align: left;
    padding: 1rem 0;
    border-bottom: 1px solid #374151;
    margin-bottom: 2rem;
}

.header-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: #f9fafb;
    margin-bottom: 0.25rem;
}

.header-subtitle {
    font-size: 0.875rem;
    color: #9ca3af;
}

.report-card {
    background: #1f2937;
    border: 1px solid #374151;
    border-radius: 4px;
    padding: 1.5rem;
    min-height: 400px;
}

.submit-btn {
    background-color: #2563eb !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 500 !important;
    border-radius: 4px !important;
    transition: background-color 0.2s;
}

.submit-btn:hover {
    background-color: #1d4ed8 !important;
}
"""

def process_query(pregunta: str):
    if not pregunta or not pregunta.strip():
        return "**Atención:** Por favor, ingresa una pregunta o consulta para iniciar la auditoría o soporte."

    # Ejecutar pipeline mediante agent.py
    reporte_markdown = run_pipeline(pregunta.strip())

    return reporte_markdown


with gr.Blocks(title="Sistema de Auditoría de Infraestructura", theme=gr.themes.Base()) as demo:

    gr.HTML("""
    <div class="header-container">
        <div class="header-title">
            Asistente de Auditoría y Soporte
        </div>
        <div class="header-subtitle">
            Plataforma de Diagnóstico de Infraestructura y Soporte Funcional
        </div>
    </div>
    """)

    with gr.Row():
        with gr.Column(scale=1):
            input_pregunta = gr.Textbox(
                label="Consulta de Soporte u Operación",
                placeholder="Ingresa los detalles del problema o la auditoría requerida...",
                lines=4,
                max_lines=6,
            )

            with gr.Row():
                btn_limpiar = gr.ClearButton([input_pregunta], value="Limpiar", variant="secondary")
                btn_enviar = gr.Button("Enviar Consulta", variant="primary", elem_classes=["submit-btn"])

            gr.Examples(
                examples=[
                    ["¿Cómo solucionar el problema de registro completado con nacionalidad extranjera incorrecta?"],
                    ["¿Qué hacer si la licencia no aparece en la aplicación pero sí en el validador?"],
                    ["¿Qué hacer si el lector RFID entra en modo Standby y deja de escanear?"],
                    ["Realizar auditoría completa del servicio de comunicación Matrix Synapse y certificados TLS."],
                    ["Diagnosticar estado de consumo de memoria, disco y procesos principales del servidor."]
                ],
                inputs=input_pregunta,
                label="Consultas Frecuentes"
            )

        with gr.Column(scale=2):
            output_reporte = gr.Markdown(
                value="*El informe técnico se desplegará aquí tras procesar la consulta.*",
                elem_classes=["report-card"]
            )

    btn_enviar.click(
        fn=process_query,
        inputs=[input_pregunta],
        outputs=[output_reporte]
    )

    input_pregunta.submit(
        fn=process_query,
        inputs=[input_pregunta],
        outputs=[output_reporte]
    )
    
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True,
        css=custom_css
    )