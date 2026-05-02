"""
Script para probar el envío de correos de aprobación/rechazo
Sin necesidad de un ERP funcional
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking.settings')
django.setup()

from django.contrib.auth.models import User
from documents.models import Document
from documents.utils import send_approval_email, send_rejection_email
from django.utils import timezone

print("\n" + "="*70)
print("🧪 TEST DE ENVÍO DE CORREOS (Modo Console - Ver en Terminal)")
print("="*70 + "\n")

# Obtener un cliente de prueba
try:
    client = User.objects.filter(profile__role='cliente').first()
    if not client:
        print("❌ No hay clientes registrados. Crea uno primero.")
        exit()
    
    print(f"✅ Cliente encontrado: {client.username} ({client.email})")
    print(f"\n{'='*70}")
    print("📧 TEST 1: Correo de APROBACIÓN")
    print("="*70)
    
    approval_reason = "CURP y RFC validados correctamente. Datos consistentes con documentos. Aprobado por SENIOR."
    
    print(f"\nEnviando correo de aprobación a: {client.email}")
    print(f"Motivo: {approval_reason}\n")
    
    send_approval_email(
        client.email,
        client.username,
        "Crédito Personal",
        approval_reason
    )
    
    print(f"\n{'='*70}")
    print("📧 TEST 2: Correo de RECHAZO")
    print("="*70)
    
    rejection_reason = "no_coinciden"
    rejection_details = "Los datos en el acta de nacimiento no coinciden con el RFC y CURP proporcionados. Por favor revisa y reenvía los documentos correctos."
    
    print(f"\nEnviando correo de rechazo a: {client.email}")
    print(f"Razón: {rejection_reason}")
    print(f"Detalles: {rejection_details}\n")
    
    send_rejection_email(
        client.email,
        client.username,
        rejection_reason,
        rejection_details
    )
    
    print(f"\n{'='*70}")
    print("✅ PRUEBA COMPLETADA")
    print("="*70)
    print("""
Los correos anteriores deberían aparecer en la consola del servidor Django.
En producción, cambiar EMAIL_BACKEND a:
  - django.core.mail.backends.smtp.EmailBackend (envío real)
  - django.core.mail.backends.locmem.EmailBackend (en memoria para testing)

Las variables de entorno requeridas:
  EMAIL_HOST=smtp.gmail.com (o tu servidor SMTP)
  EMAIL_PORT=587
  EMAIL_USE_TLS=True
  EMAIL_HOST_USER=tu_email@gmail.com
  EMAIL_HOST_PASSWORD=tu_contraseña_app
  DEFAULT_FROM_EMAIL=tu_email@gmail.com
    """)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
