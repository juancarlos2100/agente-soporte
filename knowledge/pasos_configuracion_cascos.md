# Guía de Configuración e Instalación — Dispositivo PM95 y Lector RFID RF88

## Dispositivos y Recursos Requeridos

TAGS:
configuracion
pasos
pm95
cascos
instalacion

CONTENIDO:
- **Dispositivo Móvil:** Point Mobile PM95
- **Lector RFID:** Point Mobile RF88 (identificable por número de serie)
- **Archivos APK:**
  - `com.validationapp-49306.apk` (Aplicación Validation)
  - `RFID_Control_V2_1.7.0.apk` (Controlador RFID)

---

## Fase 1: Desinstalación y Limpieza en el PM95

TAGS:
configuracion
pasos
pm95
cascos
instalacion

CONTENIDO:
1. En el dispositivo **PM95**, ubicar la aplicación **Validation**.
2. Mantener presionado sobre el icono y seleccionar **Información de la App**.
3. Ir a **Almacenamiento y Caché**.
4. Seleccionar **Borrar Caché**.
5. Regresar al menú anterior y dar tap en **Desinstalar**.

---

## Fase 2: Transferencia de Archivos APK (PC a PM95)

TAGS:
configuracion
pasos
pm95
cascos
instalacion

CONTENIDO:
1. Guardar las aplicaciones APK en la carpeta `Descargas` de la PC.
2. Conectar el dispositivo **PM95** a la PC mediante cable USB.
3. En el **PM95**: ir a **Configuración** > **Dispositivos conectados** > **USB** y seleccionar **Transferencia de Archivos**.
4. En el **Explorador de Archivos de la PC**: ubicar el dispositivo **PM95** y abrir el **Almacenamiento interno compartido**.
5. Copiar los archivos APK desde `Descargas` y pegarlos en el almacenamiento interno del PM95.
6. Desconectar el PM95 de la PC.

---

## Fase 3: Instalación de Aplicaciones en el PM95

TAGS:
configuracion
pasos
pm95
cascos
instalacion

CONTENIDO:
1. En el **PM95**, buscar y abrir la aplicación **FileTransfer**.
2. Ubicar el archivo `com.validationapp-49306.apk` y dar tap para instalar.
3. Aceptar el permiso de **Ubicación mientras la aplicación esté en uso**.
4. Regresar a **FileTransfer**.
5. Ubicar el archivo `RFID_Control_V2_1.7.0.apk` y dar tap para instalar.
6. Confirmar que ambas aplicaciones se hayan instalado correctamente.

---

## Fase 4: Vinculación y Configuración del Lector RF88

TAGS:
configuracion
pasos
pm95
cascos
instalacion

CONTENIDO:
1. Encender el lector **RF88**.
2. En el **PM95**, activar el **Bluetooth**.
3. Abrir la aplicación **RFID Control V2**.
4. Dar tap en **Search** (Buscar).
5. Ubicar y seleccionar el dispositivo **RF88** correspondiente a su número de serie.
6. Esperar a que se complete la conexión.
7. Aplicar la siguiente configuración técnica:
   - Activación: **Continuous mode** = Activado.
   - Tiempo de suspensión: **Suspend timeout** = `0` (cero).
   - Confirmación: Dar tap en **Apply**.
   - Perfil de usuario: Seleccionar **Perfil** y activar **User defined**.

---

## Resumen de Pasos para Diagnóstico Rápido

TAGS:
configuracion
pasos
pm95
cascos
instalacion

CONTENIDO:

| Fase | Acción Principal | Detalle Técnico |
|---|---|---|
| **1. Limpieza** | Desinstalar Validation previa | Borrar caché antes de desinstalar |
| **2. Transferencia** | Copiar APKs vía USB | Guardar en Almacenamiento Interno Compartido |
| **3. Instalación** | Instalar APKs vía FileTransfer | Permitir ubicación en uso para Validation |
| **4. Vinculación** | Conectar RF88 por Bluetooth | Buscar por Número de Serie en RFID Control |
| **5. Ajustes RFID** | Configurar parámetros del lector | `Continuous mode = ON`, `Suspend timeout = 0`, `Profile = User defined` |
