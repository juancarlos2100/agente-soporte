# Base de Conocimiento - Casos Frecuentes de Soporte

## 1. Licencia visible en el validador pero no en la aplicación

TAGS:
licencia
holograma
validador
casco
ciudadano

CONTENIDO:

### Síntoma
La licencia aparece correctamente en el validador de licencias, pero no se muestra dentro de la aplicación.

### Procedimiento
1. Generar un archivo Excel con la información del ciudadano.
2. Capturar toda la información correspondiente.
3. Tomar una fotografía del casco donde sea visible el holograma pegado.
4. Adjuntar la evidencia para seguimiento.

### Validación Importante
- **Tipo de Licencia:** Verificar rigurosamente que la licencia presentada sea de **motociclista**. Se han detectado casos erróneos donde el ciudadano presenta una licencia **mercantil**, la cual no es válida para este trámite.

### Evidencia requerida
- Archivo Excel con los datos del ciudadano.
- Fotografía del casco con holograma visible.

---

## 2. Carta de consentimiento

TAGS:
consentimiento
impresa
original
carta

CONTENIDO:

### Requisito
La carta consentimiento debe presentarse en formato original impreso.

### Validación
Verificar que la carta entregada corresponda al documento original y no a copias digitales o fotocopias.

---

## 3. Registro completado con nacionalidad extranjera incorrecta

TAGS:
registro
extranjera
nacionalidad
extranjero



CONTENIDO:

### Síntoma
El trámite se realiza correctamente, pero al finalizar el registro aparece como nacionalidad extranjera.

### Causa conocida
Este comportamiento se origina en los servicios o API del gobierno.

### Impacto
No impide completar ni registrar el trámite.

### Acción recomendada
Informar al usuario que el registro fue realizado correctamente y que el problema corresponde a información proveniente de servicios externos.

---

## 4. Mensaje: "Conexión inestable o lenta"

TAGS:
red
falla
inestable
conexion
internet
lenta

CONTENIDO:

### Síntoma
Durante el uso de la aplicación aparece el mensaje:

> Conexión inestable o lenta

### Causa probable
Problemas de conectividad o baja calidad de red.

### Validación
Realizar pruebas de velocidad y estabilidad de internet.

### Herramientas de validación
- [Cloudflare Speed Test](https://speed.cloudflare.com/)
- [Fast.com](https://fast.com/es/)

---

## 5. Error de inicio de sesión por falta de conectividad

TAGS:
soporte
configuracion

CONTENIDO:

### Síntoma
Al iniciar sesión con credenciales correctas aparece el mensaje:

> No tienes conexión a internet o tus datos se han agotado. Verifica tu conexión e intenta de nuevo.

### Causa probable
La red es inestable o no existe conectividad activa.

### Validación
Realizar pruebas de velocidad y conectividad utilizando:

- [Cloudflare Speed Test](https://speed.cloudflare.com/)
- [Fast.com](https://fast.com/es/)

### Acción recomendada
Verificar que el dispositivo tenga acceso estable a internet antes de intentar nuevamente el inicio de sesión.

---

## 6. Error de vinculación de RFID

TAGS:
rfid
pistola
distintivo
tid
lector
vinculacion

CONTENIDO:

### Síntoma
Durante el escaneo del distintivo aparece el mensaje:

> Error al vincular RFID, el RFID no existe o no está disponible para vinculación.

Además se muestra:

> TID FÍSICO LEÍDO:

### Causa conocida
El distintivo RFID no ha sido asignado al módulo correspondiente.

### Validación
Verificar la asignación del distintivo dentro del sistema de administración correspondiente.

### Acción recomendada
Confirmar que el RFID se encuentre registrado y asignado al módulo correcto antes de intentar nuevamente la vinculación.

---

## 7. Fallas en la aplicación con red estable

TAGS:
red
falla
inestable
conexion
internet
lenta

CONTENIDO:

### Síntoma
La aplicación presenta fallas o comportamiento inestable a pesar de contar con una conexión de red activa y estable.

### Procedimiento
1. Ingrese a **Configuración** del dispositivo.
2. Acceda a **Aplicaciones** y seleccione **Validaciones App**.
3. Pulse **Forzar detención**.
4. Seleccione **Borrar caché**.
5. Posteriormente, seleccione **Borrar datos**.
6. Abra nuevamente la aplicación e inicie sesión.
7. Verifique si el inconveniente ha sido resuelto.

---

## 8. Suspensión o modo Standby de la pistola RFID

TAGS:
rfid
pistola
distintivo
tid
lector
vinculacion

CONTENIDO:

### Síntoma
El lector RFID deja de responder o escanear tras varios intentos fallidos.

### Causa conocida
Después de varios intentos fallidos de escaneo, la pistola RFID entra automáticamente en modo **Standby** como medida de ahorro de energía.

### Acción recomendada
Encender nuevamente el dispositivo (lector RFID) físicamente para reanudar las operaciones de escaneo y reestablecer el enlace.

---

# Lista rápida de diagnóstico

| Síntoma | Validación inicial |
|----------|----------|
| Licencia no aparece en la app | Generar Excel + foto de casco con holograma |
| Carta consentimiento | Verificar que sea original impresa |
| Nacionalidad extranjera incorrecta | Corresponde a servicios externos; no bloquea el registro |
| Conexión inestable o lenta | Validar velocidad de internet |
| No tienes conexión a internet o tus datos se han agotado | Validar conectividad y velocidad de red |
| Error al vincular RFID | Verificar asignación del distintivo al módulo |
| App falla con red estable | Forzar detención + Borrar caché y datos + Reiniciar sesión |
| Pistola RFID deja de escanear (Standby) | Encender físicamente el lector RFID de nuevo |