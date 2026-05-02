"""
Django management command para probar envío de correos
Uso: python manage.py test_approval_emails
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from documents.utils import send_approval_email, send_rejection_email

class Command(BaseCommand):
    help = 'Prueba el envío de correos de aprobación/rechazo'

    def handle(self, *args, **options):
        print("\n" + "="*70)
        print("🧪 TEST DE ENVÍO DE CORREOS (Modo Console)")
        print("="*70 + "\n")

        # Obtener un cliente de prueba
        client = User.objects.filter(profile__role='cliente').first()
        if not client:
            self.stdout.write(self.style.ERROR("❌ No hay clientes registrados. Crea uno primero."))
            return

        self.stdout.write(self.style.SUCCESS(f"✅ Cliente encontrado: {client.username} ({client.email})"))
        
        # TEST 1: Correo de aprobación
        self.stdout.write("\n" + "="*70)
        self.stdout.write(self.style.WARNING("📧 TEST 1: Correo de APROBACIÓN"))
        self.stdout.write("="*70 + "\n")
        
        approval_reason = "CURP y RFC validados correctamente. Datos consistentes con documentos. Aprobado por SENIOR."
        
        self.stdout.write(f"Enviando correo de aprobación a: {client.email}")
        self.stdout.write(f"Motivo: {approval_reason}\n")
        
        result = send_approval_email(
            client.email,
            client.username,
            "Crédito Personal",
            approval_reason
        )
        
        if result:
            self.stdout.write(self.style.SUCCESS("✅ Correo de aprobación enviado (ver arriba en la consola)"))
        else:
            self.stdout.write(self.style.ERROR("❌ Error al enviar correo de aprobación"))
        
        # TEST 2: Correo de rechazo
        self.stdout.write("\n" + "="*70)
        self.stdout.write(self.style.WARNING("📧 TEST 2: Correo de RECHAZO"))
        self.stdout.write("="*70 + "\n")
        
        rejection_reason = "no_coinciden"
        rejection_details = "Los datos en el acta de nacimiento no coinciden con el RFC y CURP proporcionados. Por favor revisa y reenvía los documentos correctos."
        
        self.stdout.write(f"Enviando correo de rechazo a: {client.email}")
        self.stdout.write(f"Razón: {rejection_reason}")
        self.stdout.write(f"Detalles: {rejection_details}\n")
        
        result = send_rejection_email(
            client.email,
            client.username,
            rejection_reason,
            rejection_details
        )
        
        if result:
            self.stdout.write(self.style.SUCCESS("✅ Correo de rechazo enviado (ver arriba en la consola)"))
        else:
            self.stdout.write(self.style.ERROR("❌ Error al enviar correo de rechazo"))
        
        self.stdout.write("\n" + "="*70)
        self.stdout.write(self.style.SUCCESS("✅ PRUEBA COMPLETADA"))
        self.stdout.write("="*70 + "\n")
        
        self.stdout.write(self.style.HTTP_INFO("""
Los correos anteriores deberían aparecer arriba en la consola.

En producción, cambiar EMAIL_BACKEND a:
  - django.core.mail.backends.smtp.EmailBackend (envío real)
  - django.core.mail.backends.locmem.EmailBackend (en memoria para testing)

Ver EMAIL_SETUP.md para instrucciones de configuración completa.
        """))
