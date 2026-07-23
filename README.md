**InfraBot** es una plataforma de soporte técnico y auditoría asistida por IA que combina modelos LLM locales ejecutados mediante Ollama, recuperación de conocimiento (RAG), procesamiento de lenguaje natural y automatización de evidencias para responder consultas operativas, procedimientos de soporte y auditorías de infraestructura.

El sistema funciona completamente en entorno local, sin depender de servicios externos, permitiendo analizar documentación interna, recopilar evidencias técnicas y generar respuestas contextualizadas para usuarios de soporte, operaciones e infraestructura.

---

# Características

## Soporte Técnico Inteligente

- Consulta procedimientos operativos documentados.
- Respuesta basada exclusivamente en documentación interna.
- Escalamiento automático a soporte humano cuando no existe información suficiente.
- Clasificación automática de intención.
- Recuperación inteligente de conocimiento mediante búsqueda contextual.

Ejemplos:

```text
¿Qué hago si la licencia aparece en el validador pero no en la aplicación?

¿Por qué no puedo vincular un distintivo RFID?

¿La carta consentimiento puede ser copia?

¿Qué significa conexión inestable o lenta?
```

---

## Auditoría de Infraestructura

Permite realizar auditorías asistidas mediante evidencia real obtenida desde servidores remotos.

Capaz de analizar:

- Memoria RAM
- Almacenamiento
- Uptime
- Procesos activos
- Estado de Matrix
- Certificados TLS
- Versiones de servicios
- Kubernetes
- Helm
- Jobs
- Pods

Ejemplos:

```text
¿Cómo está Matrix?

¿Existen problemas de memoria?

Audita el estado completo del servidor.

Verifica el estado interno de ESS.
```

---

## Base de Conocimiento Local

InfraBot utiliza documentación interna almacenada en:

```text
knowledge/
```

Los documentos son procesados mediante:

- TAGS
- Normalización de texto
- Sinónimos de dominio
- Ranking por relevancia
- Recuperación contextual

Formatos compatibles:

```text
.md
.txt
```

---

## Seguridad

InfraBot fue diseñado bajo un modelo de privilegios seguros:

Auditorías de solo lectura
No ejecuta cambios sobre infraestructura
No posee privilegios sudo
Evidencias privilegiadas requieren validación humana
Implementación completamente local

---

# Arquitectura

```text
Usuario
    │
    ▼
 Planner
    │
    ▼
 Collector
    │
    ├── Infraestructura
    ├── Knowledge Base
    └── Evidencia Privilegiada
    │
    ▼
 Analyst
    │
    ▼
 Respuesta / Reporte
```

---

#  Componentes

## Planner

Responsable de:

- Clasificar intención
- Seleccionar evidencias necesarias
- Diferenciar entre:
  - Soporte técnico
  - Infraestructura
  - Auditoría

Salida:

```json
{
  "intent": "support",
  "evidences": [
    "knowledge_search"
  ]
}
```

---

## Collector

Responsable de:

- Recolectar evidencias de infraestructura
- Consultar documentación interna
- Gestionar evidencias pendientes
- Administrar comandos privilegiados
- Recuperar información relevante

---

## Analyst

Responsable de:

- Interpretar evidencias
- Analizar documentación
- Generar diagnósticos
- Elaborar reportes
- Responder consultas de soporte

---

#  Estructura del Proyecto

```text
infra-lab/
│
├── knowledge/
│   ├── configuracion_rfid.md
│   ├── messages.md
│   └── pasos_configuracion_cascos.md
│
├── evidence/
│   ├── knowledge/
│   ├── server/
│   ├── matrix/
│   ├── kubernetes/
│   ├── logs/
│   └── postgres/
│
├── reports/
│
├── commands/
│
├── planner.py
├── collector.py
├── analyst.py
├── agent.py
├── tools.py
├── knowledge_synonyms.py
└── app.py
```

---

# Interfaz Web

InfraBot incluye una interfaz web basada en Gradio.

Iniciar:

```bash
python app.py
```

Acceso local:

```text
http://127.0.0.1:7860
```

Acceso LAN:

```text
http://<IP_LOCAL>:7860
```

---

# Tecnologías Utilizadas

- Python
- Ollama
- Qwen / Llama
- Gradio
- SSH
- Markdown Knowledge Base
- Retrieval-Augmented Generation (RAG)
- NLP básico
- JSON
- PowerShell

---

# Casos de Uso

## Soporte Técnico

- RFID
- Licencias
- Conectividad
- Configuración de dispositivos
- Procedimientos operativos

## Infraestructura

- Linux
- Matrix
- Synapse
- Kubernetes
- Helm
- Certificados TLS

## Operaciones

- Auditorías
- Validación de configuraciones
- Diagnóstico de incidencias
- Consulta de procedimientos

---

# Roadmap

- [ ] Memoria conversacional
- [ ] Retrieval semántico avanzado
- [ ] NLP con spaCy
- [ ] Similaridad difusa con RapidFuzz
- [ ] Integración Matrix/Element
- [ ] PostgreSQL/MAS
- [ ] Soporte multiusuario por sesión
- [ ] Dashboard operativo
- [ ] Reportes ejecutivos avanzados

---

# Licencia

Proyecto experimental para soporte técnico, automatización operativa y auditoría asistida por IA.

@author JUAN CARLOS MEJIA ARGUELLO 

---

**InfraBot** — Soporte Técnico y Auditoría de Infraestructura impulsados por IA local.
