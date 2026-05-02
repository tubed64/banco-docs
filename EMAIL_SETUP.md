# 📧 Configuración de Envío de Correos

## Estado Actual
- ✅ Los correos se envían **independientemente del ERP**
- ✅ Se envían cuando se **APRUEBA** (con motivo de aprobación)
- ✅ Se envían cuando se **RECHAZA** (con razón y detalles)
- ✅ Django está configurado con **Console Backend** (desarrollo)

## 🧪 Probar los Correos en Desarrollo

### Opción 1: Script de Prueba Rápida
```bash
python manage.py shell < test_emails_approval.py
```

Este script simula:
1. Un correo de **aprobación** con motivo
2. Un correo de **rechazo** con razón y detalles

Los correos aparecerán en la **terminal del servidor Django** (donde corre `runserver`).

### Opción 2: Usando la Interfaz Web
1. Ingresa como usuario **SENIOR**
2. Ve a un documento en revisión
3. Click en "Aprobar"
4. En el modal, ingresa un motivo de aprobación
5. Confirma
6. **Revisa la terminal del servidor** - verás el correo impreso

## 📩 Flujo de Correos Actual

### APROBACIÓN (SENIOR aprueba):
```
1. SENIOR ingresa motivo en el formulario
2. Se valida el documento
3. Se ENVÍA CORREO al cliente ✅ (AQUÍ)
4. Se intenta exportar a ERP
   - Si éxito: mensaje "Correo enviado y ERP actualizado"
   - Si falla: mensaje "Correo enviado (ERP no disponible)"
```

### RECHAZO (STAFF o SENIOR rechaza):
```
1. Validador selecciona razón + detalles
2. Se ENVÍA CORREO al cliente ✅ (AQUÍ)
3. Documento se marca como rechazado
```

## 🚀 Configurar para Producción (Correos Reales)

### Usando Gmail:

#### Paso 1: Configurar Gmail
1. Habilitar "Aplicaciones menos seguras" en tu cuenta Google
   - O usar una **contraseña de aplicación** (recomendado)
   - [Generar contraseña de aplicación](https://myaccount.google.com/apppasswords)

#### Paso 2: Agregar Variables de Entorno
En `.env` o en tu servidor:
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_contraseña_app
DEFAULT_FROM_EMAIL=tu_email@gmail.com
```

#### Paso 3: Actualizar settings.py (ya está configurado)
```python
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "banco@validacion.com")
```

### Usando SendGrid (Alternativa):
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.tu_sendgrid_key
DEFAULT_FROM_EMAIL=tu_email@tudominio.com
```

### Usando Amazon SES:
```
pip install django-ses
EMAIL_BACKEND=django_ses.SESBackend
AWS_SES_REGION_NAME=us-east-1
AWS_SES_REGION_ENDPOINT=email.us-east-1.amazonaws.com
AWS_ACCESS_KEY_ID=tu_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key
```

## 📊 Resumen de Cambios

### ✅ Cambios Realizados:
1. **Desacoplamiento de Correos y ERP**
   - Correos se envían ANTES de intentar exportar a ERP
   - Si ERP falla, el cliente igual recibe su correo

2. **Independencia de Funcionalidad**
   - STAFF puede revisar (sin enviar correos todavía)
   - SENIOR aprueba/rechaza:
     - Si APRUEBA: se envía correo + intenta ERP
     - Si RECHAZA: se envía correo con motivo

3. **Mejores Mensajes**
   - Si ERP funciona: "Correo enviado y datos exportados a ERP"
   - Si ERP no funciona: "Correo enviado (Nota: ERP no disponible)"

## 🧠 Funciones Clave

### `send_approval_email(email, name, credit_type, approval_reason)`
Envía correo de aprobación con:
- Nombre del cliente
- Tipo de crédito
- **Motivo de aprobación**
- Indicación de próximos pasos

### `send_rejection_email(email, name, reason, details)`
Envía correo de rechazo con:
- Razón del rechazo (con emoji)
- Detalles específicos del rechazo
- Indicación de cómo corregir

## 🔧 Troubleshooting

### Los correos no aparecen en la consola
- ✅ Asegúrate de que Django está usando `console.EmailBackend`
- ✅ Revisa la terminal donde corre `python manage.py runserver`
- ✅ Los correos pueden estar en el log de Django

### En producción, los correos no se envían
- ✅ Verifica las credenciales SMTP
- ✅ Revisa los logs de Django (ADMINS email)
- ✅ Usa Django Debug Toolbar para ver excepciones
- ✅ Prueba la conexión SMTP:
  ```python
  from django.core.mail import send_mail
  send_mail('Test', 'Contenido', 'from@example.com', ['to@example.com'])
  ```

## 📝 Ejemplo de Correo Generado

```
Hola cliente_test,

¡Excelentes noticias! Tu solicitud de Crédito Personal ha sido aprobada.

Motivo de Aprobación:
CURP y RFC validados correctamente. Datos consistentes con documentos. Aprobado por SENIOR.

Tu solicitud ha sido registrada en nuestro sistema. Próximamente nos pondremos en contacto contigo con los detalles de tu aprobación.

Gracias por tu confianza,
Equipo de Validación Bancaria
```
