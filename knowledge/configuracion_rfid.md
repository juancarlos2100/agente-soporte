# Reporte Técnico y Guía de Configuración — Lector RFID Point Mobile RF88 y Terminal PM85

## Información General

TAGS:
soporte
configuracion

CONTENIDO:
- **Fecha de Evaluación:** 26 de Junio de 2026
- **Dispositivos Implicados:** Lector RFID Point Mobile RF88, Terminal Portátil PM85 y PM95
- **Entorno de Integración:** App *RFID Control (V2)* y desarrollo de terceros (*SCP Police*)

---

## 1. Objetivo del Reporte

TAGS:
soporte
configuracion

CONTENIDO:
Documentar el comportamiento operativo, las limitaciones de configuración masiva mediante JSON y las estrategias de optimización para el lector **Point Mobile RF88** acoplado al terminal **PM85**. El objetivo principal es lograr lecturas individuales precisas, reducir la latencia de transmisión y estandarizar la configuración en múltiples terminales.

---

## 2. Análisis del Protocolo Anticolisión (Algoritmo Q)

TAGS:
soporte
configuracion

CONTENIDO:
Los parámetros **Query (Q)** no controlan la distancia de lectura, sino la lógica algorítmica de la norma EPC Gen2 para procesar múltiples etiquetas simultáneamente mediante turnos aleatorios ($0$ a $2^Q - 1$).

- **Para Inventarios Masivos:** Activar `INCREMENT_Q = "1"` y `DECREMENT_Q = "1"`. Esto permite que el algoritmo escale o reduzca dinámicamente el valor de Q según la densidad de etiquetas en el entorno.
- **Para Lecturas Únicas (Aislamiento de Tag):** Fijar `START_Q = "0"`, `MIN_Q = "0"`, `MAX_Q = "0"` y congelar la adaptación con `FIXED_Q = "1"`. Esto elimina el tiempo de espera del algoritmo, logrando una singularización casi instantánea cuando queda una sola etiqueta.

---

## 3. Aislamiento Físico de Lectura (Potencia de Antena)

TAGS:
soporte
configuracion
potencia
power
dbm
alcance
distancia
rf88
lector
rfid
pistola
db

CONTENIDO:
Para garantizar la lectura de un solo tag en entornos densos, el ajuste por software (algoritmo Q) debe complementarse en la capa física mediante los decibelios (**dBm**):

- **Comportamiento por defecto:** `30.0 dBm` (Lectura omnidireccional de alto alcance).
- **Estrategia de aislamiento:** Reducir la potencia (ej. `10.0` a `15.0 dBm`) desde la aplicación *RFID Control* en `Profile` > `User defined` > `Power`. Esto colapsa el campo electromagnético, obligando a acercar el lector a extrema proximidad del tag deseado y eliminando la lectura no deseada de etiquetas vecinas.

---

## 4. Arquitectura del Archivo de Configuración Masiva (`RF88-Configuration.json`)

TAGS:
soporte
configuracion

CONTENIDO:
La herramienta web *RFIDControl Configuration Tool* y la aplicación móvil parsean **todos los valores del archivo JSON estrictamente como strings**, independientemente del tipo de dato lógico subyacente.

### Diccionario de Datos Extendido: `RF88-Configuration.json`

| Parámetro JSON | Valores Posibles (String) | Efecto al Aumentar / Activar ("1") | Efecto al Disminuir / Desactivar ("0") |
|---|---|---|---|
| `START_Q` | `"0"` a `"15"` | Asume entorno masivo inicial. Evita colisiones pero retrasa lecturas de pocos tags. | Asume entorno despejado. Acelera lectura inicial (ideal en `"0"` para un solo tag). |
| `MIN_Q` | `"0"` a `"15"` | Fuerza piso de turnos. Ralentiza el final del inventario con pocas etiquetas. | Permite llegar a cero turnos, logrando singularización instantánea para 1 tag. |
| `MAX_Q` | `"0"` a `"15"` | Permite al algoritmo escalar en almacenes masivos con miles de tags. | Limpia el techo. Si hay demasiadas etiquetas y Q es muy bajo, puede haber choques. |
| `INCREMENT_Q` | `"1"` o `"0"` | **("1")** Auto-incrementa Q dinámicamente si detecta colisiones de datos. | **("0")** No reacciona ante colisiones masivas, perdiendo eficiencia en multitudes. |
| `DECREMENT_Q` | `"1"` o `"0"` | **("1")** Auto-reduce Q si detecta silencios (pocas etiquetas), agilizando el proceso. | **("0")** Mantiene turnos vacíos innecesarios, perdiendo tiempo. |
| `FIXED_Q` | `"1"` o `"0"` | **("1")** Congela el valor Q en `START_Q`, ignorando el entorno dinámico. | **("0")** Permite al lector adaptarse dinámicamente mediante incremento/decremento. |
| `INVENTORY_RESPONSE` | `"0"`, `"1"`, `"2"`... | **(Mayor)** Solicita más datos (ej. RSSI), haciendo el payload más pesado y lento. | **(Menor)** Solicita solo el código EPC, haciendo el payload ligero y la lectura rápida. |
| `CONTINUOUS` | `"c"` o `"p"` | **("c")** Emisión continua sin soltar gatillo (mayor consumo y lecturas duplicadas). | **("p")** Lectura por pulsación controlada (evita saturación de la interfaz). |
| `VOLUME` | `"0"`, `"1"`, `"2"` | Mayor volumen de confirmación auditiva para entornos ruidosos. | `"0"` silencia por completo las confirmaciones audibles de hardware. |
| `KEY_MAP` | String | Reasigna funciones a los gatillos físicos del dispositivo. | N/A (configuración por defecto). |
| `VIBRATE` | `"1"` o `"0"` | **("1")** El motor háptico vibra al confirmar cada lectura exitosa. | **("0")** Desactiva la respuesta de vibración física. |
| `SUSPEND_TIME` | `"0"` a `"30"` | Minutos de inactividad antes de suspender Bluetooth (ahorra batería; `"0"` = nunca). | `"0"` mantiene la conexión Bluetooth siempre activa sin suspensión. |
| `AUTO_UPDATE` | `"1"` o `"0"` | **("1")** Reprograma el lector automáticamente con el JSON al conectar. | **("0")** Respeta la configuración actual del lector sin forzar sobrescritura. |
| `RFU_FILE_NAME` | String o `""` | Especifica un archivo firmware `.rfu` para actualización del sistema. | `""` ignora actualización de firmware y solo aplica parámetros. |

---

## 5. Jerarquía de Control y Sobrescritura por Aplicaciones de Terceros (SDK/API)

TAGS:
soporte
configuracion

CONTENIDO:
Al integrar aplicaciones personalizadas (*Custom Apps*) mediante el SDK nativo de Point Mobile o Intents:

1. **El archivo JSON es una Línea Base (Baseline):** Las configuraciones inyectadas mediante `RF88-Configuration.json` actúan estrictamente como estado por defecto en arranque en frío.
2. **Prioridad de Ejecución en Tiempo Real (SDK Override):** Si la aplicación de terceros inicializa el escáner y envía sus propios parámetros (potencia, algoritmo Q, perfiles de enlace o máscaras), **estos comandos sobrescriben y anulan inmediatamente la configuración del JSON local**.

---

## 6. Flujo de Trabajo para Configuración y Despliegue del JSON

TAGS:
soporte
configuracion

CONTENIDO:

### 6.1. Método Gráfico (Vía *RFIDControl Configuration Tool*)
*Ideal para personal de soporte y operaciones.*
1. Descargar el archivo `.zip` de *RFIDControl Configuration Tool (V2)* desde el portal de servicio.
2. Descomprimir y abrir el archivo `index.html` en Google Chrome.
3. Ajustar visualmente los parámetros de RFID, Hardware y Auto Update.
4. Hacer clic en **Export** para descargar el archivo JSON validado.

### 6.2. Método de Desarrollo (Edición Directa en IDE / VS Code)
*Recomendado para equipos de ingeniería.*
1. **Exportación Base:** En un PM85 con RF88 conectado, configurar parámetros en la app *RFID Control (V2)* > Menú **Configuration** > Título > **Export**.
2. **Extracción:** Conectar PM85 a la PC y copiar el archivo desde `/storage/emulated/0/Download/`.
3. **Edición:** Abrir `RF88-Configuration.json` en VS Code.
   > **Regla de Oro:** Todos los valores en el JSON deben formatearse estrictamente como `string` (ej. `"1"` en lugar de `1`, `"0"` en lugar de `false`).
4. **Validación:** Confirmar la sintaxis del JSON antes de guardar.

---

## 7. Despliegue en el PM85 (Auto Update)

TAGS:
soporte
configuracion

CONTENIDO:
Para aplicar la configuración en el terminal PM85:

1. Copiar el archivo generado al PM85 vía USB.
2. **Ruta Obligatoria:** `/storage/emulated/0/Download/` (carpeta `/Download/`).
3. **Nombre Obligatorio:** Debe nombrarse exactamente `RF88-Configuration.json`.
4. **Ejecución:** Si `AUTO_UPDATE` está en `"1"`, la app *RFID Control* reprogramará el lector RF88 automáticamente al conectarse por Bluetooth o acoplamiento físico.

---

## 8. Validación de Funcionamiento (Prueba de Estado Base)

TAGS:
soporte
configuracion

CONTENIDO:
Se ejecutó una prueba funcional base para establecer el punto de rendimiento máximo:

- **Parámetros Aplicados:** Potencia = `30.0 dBm`, Sesión = `S0`, Flag = `A`.
- **Resultado:** Respuesta inmediata de lectura en la app *Rapid Read Demo*, sin latencia y con refresco instantáneo de estado (S0).
- **Observación sobre Alcance:** Reducir la potencia en dBm no mostró disminuciones proporcionales en la distancia de lectura en entornos cerrados, debido a la alta sensibilidad de la antena frente a reflexiones electromagnéticas del entorno.

---

## 9. Hallazgos Empíricos en Integración con App de Terceros (*SCP Police*)

TAGS:
soporte
configuracion

CONTENIDO:
En pruebas de campo con la aplicación de terceros integrada vía SDK, se observaron comportamientos diferentes al estado base:

- **Restricción de Alcance:** Distancia efectiva limitada a **$\le$ 5 cm**. La app de terceros fuerza un perfil de radiofrecuencia (Link Profile) de baja energía/alta selectividad que sobrescribe el hardware.
- **Latencia de Respuesta:** Tiempo de lectura de **~3 segundos** por tag. Indica que la app ejecuta un ciclo de interrogación estructurado con filtrado por máscara o handshake de validación antes de confirmar la lectura.

---

## 10. Conclusión Final

TAGS:
soporte
configuracion

CONTENIDO:

- La reducción manual de decibelios (dBm) vía JSON o GUI es insuficiente si una aplicación de terceros toma el control del lector mediante el SDK.
- La distancia de lectura (5 cm) y la latencia (~3 s) registradas en campo son dictadas por el código de la app de terceros (SDK/Link Profile/Mask).
- **Acción Recomendada:** Para modificar el alcance o la velocidad de lectura en producción, los ajustes deben realizarse directamente en el código fuente de la aplicación de terceros.

---

## Resumen de Parámetros Clave para Diagnóstico Rápido

TAGS:
soporte
configuracion

CONTENIDO:

| Objetivo | Parámetros Recomendados |
|---|---|
| **Lectura de 1 solo Tag (Aislamiento)** | `START_Q="0"`, `MIN_Q="0"`, `MAX_Q="0"`, `FIXED_Q="1"`, `Power=10.0-15.0 dBm` |
| **Inventario Masivo Dinámico** | `INCREMENT_Q="1"`, `DECREMENT_Q="1"`, `FIXED_Q="0"`, `Power=30.0 dBm` |
| **Lectura Rápida (Payload ligero)** | `INVENTORY_RESPONSE="0"` (Solo EPC), `CONTINUOUS="p"` |
| **Despliegue Automático en PM85** | Ruta: `/Download/RF88-Configuration.json`, `AUTO_UPDATE="1"` |
| **Todos los valores JSON** | Deben formatearse como `string` (ej. `"1"`, `"0"`) |
