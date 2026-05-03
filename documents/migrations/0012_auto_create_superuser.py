import os
from django.contrib.auth import get_user_model
from django.db import migrations

def create_superuser(apps, schema_editor):
    User = get_user_model()
    try:
        if not User.objects.filter(is_superuser=True).exists():
            username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
            email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
            password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "admin123")
            
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            # Configurar como admin
            if hasattr(user, 'profile'):
                user.profile.role = "admin"
                user.profile.is_worker = True
                user.profile.save()
            print(f"Superusuario '{username}' creado automáticamente con rol admin")
    except Exception as e:
        print(f"Error creando superusuario: {e}")

class Migration(migrations.Migration):
    dependencies = [
        ('documents', '0011_document_clicked_continuidad'),
    ]
    operations = [
        migrations.RunPython(create_superuser),
    ]
