import os
from django.contrib.auth import get_user_model
from django.db import migrations

def create_users(apps, schema_editor):
    User = get_user_model()
    try:
        # Crear superusuario admin
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
        
        # Crear validador1 (STAFF)
        if not User.objects.filter(username="validador1").exists():
            v1 = User.objects.create_user(
                username="validador1",
                email="validador1@banco.com",
                password="validate123"
            )
            if hasattr(v1, 'profile'):
                v1.profile.role = "validator1"
                v1.profile.is_worker = True
                v1.profile.save()
            print("Validador1 creado")
            
        # Crear validador2 (SENIOR)
        if not User.objects.filter(username="validador2").exists():
            v2 = User.objects.create_user(
                username="validador2",
                email="validador2@banco.com",
                password="validate123"
            )
            if hasattr(v2, 'profile'):
                v2.profile.role = "validator2"
                v2.profile.is_worker = True
                v2.profile.save()
            print("Validador2 creado")
            
    except Exception as e:
        print(f"Error creando usuarios: {e}")

class Migration(migrations.Migration):
    dependencies = [
        ('documents', '0011_document_clicked_continuidad'),
    ]
    operations = [
        migrations.RunPython(create_users),
    ]
