TOOLS = {
    "memory": {
        "type": "automatic",
        "category": "server",
        "command": "free -h",
        "file": "memory.txt",
        "description": "Estado de memoria RAM"
    },

    "disk": {
        "type": "automatic",
        "category": "server",
        "command": "df -h /",
        "file": "disk.txt",
        "description": "Uso de almacenamiento"
    },

    "uptime": {
        "command": "uptime",
        "file": "uptime.txt",
        "description": "Muestra el tiempo activo del sistema y la carga promedio"
    },

    "top_processes": {
        "type": "automatic",
        "category": "server",
        "command": "ps aux --sort=-%cpu | head -20",
        "file": "top_processes.txt",
        "description": "Procesos con mayor consumo"
    },

    "matrix_version": {
        "type": "automatic",
        "category": "matrix",
        "command": "curl -s https://matrix.implemx.com/_matrix/client/versions",
        "file": "matrix_version.json",
        "description": "Obtiene las versiones soportadas por Matrix y confirma que Synapse responde correctamente"
    },

    "matrix_health": {
        "type": "automatic",
        "category": "matrix",
        "command": "curl -s -o /dev/null -w '%{http_code}' https://matrix.implemx.com/_matrix/client/versions",
        "file": "matrix_health.txt",
        "description": "Verifica si la API principal de Matrix responde correctamente mediante un código HTTP"
    },

    "matrix_tls": {
        "type": "automatic",
        "category": "matrix",
        "command": "echo | openssl s_client -connect matrix.implemx.com:443 -servername matrix.implemx.com 2>/dev/null | openssl x509 -noout -issuer -subject",
        "file": "matrix_tls.txt",
        "description": "Verifica el certificado TLS de Matrix, incluyendo emisor y sujeto"
    },

    "pods": {
        "type": "privileged",
        "category": "kubernetes",
        "command": "sudo k3s kubectl get pods -n ess",
        "file": "pods.txt",
        "description": "Lista los pods del namespace ess en Kubernetes"
    },

    "jobs": {
        "type": "privileged",
        "category": "kubernetes",
        "command": "sudo k3s kubectl get jobs -n ess",
        "file": "jobs.txt",
        "description": "Lista los jobs del namespace ess en Kubernetes"
    },

    "helm_status": {
        "type": "privileged",
        "category": "kubernetes",
        "command": "sudo env KUBECONFIG=/etc/rancher/k3s/k3s.yaml helm status ess -n ess",
        "file": "helm_status.txt",
        "description": "Muestra el estado del release Helm ess"
    },
    
    "knowledge_search": {
        "type": "knowledge",
        "category": "knowledge",
        "command": "internal_knowledge_search",
        "file": "knowledge_results.txt",
        "description": "Busca respuestas en la base de conocimientos sobre procedimientos, configuraciones, manuales, soporte técnico y preguntas frecuentes"
    }
}
