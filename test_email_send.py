import os
from pathlib import Path
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking.settings')
BASE_DIR = Path(__file__).resolve().parent.parent
from dotenv import load_dotenv
load_dotenv(BASE_DIR / ".env")

django.setup()

from django.conf import settings
from django.core.mail import send_mail

# Mostrar configuración actual
print("=== Configuración de Email ===")
print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"EMAIL_HOST_PASSWORD: {'***' + settings.EMAIL_HOST_PASSWORD[-4:] if settings.EMAIL_HOST_PASSWORD else 'VACÍO'}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
print()

# Obtener usuarios con email
from django.contrib.auth.models import User
users = User.objects.exclude(email='')
print("=== Usuarios con email ===")
for user in users:
    print(f"  - {user.username}: {user.email}")
print()

if users.exists():
    user = users.first()
    print(f"=== Enviando correo de prueba a {user.email} ===")
    try:
        send_mail(
            'Correo de prueba',
            'Este es un correo de prueba del sistema de validación bancaria.',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        print("SUCCESS: Correo enviado exitosamente!")
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("❌ No hay usuarios con email registrado")
