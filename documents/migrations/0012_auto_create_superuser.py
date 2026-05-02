import os
from django.contrib.auth import get_user_model
from django.db import migrations

def create_superuser(apps, schema_editor):
    User = get_user_model()
    if not User.objects.filter(is_superuser=True).exists():
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "admin123")
        
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"Superusuario '{username}' creado automáticamente")

class Migration(migrations.Migration):
    dependencies = [
        ('documents', '0011_document_clicked_continuidad'),
    ]
    operations = [
        migrations.RunPython(create_superuser),
    ]
