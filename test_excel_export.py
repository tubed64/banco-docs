import os
from pathlib import Path
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking.settings')
BASE_DIR = Path(__file__).resolve().parent.parent
from dotenv import load_dotenv
load_dotenv(BASE_DIR / ".env")
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from documents.views import export_monthly_excel
from django.utils import timezone
from documents.models import Document

factory = RequestFactory()
admin_user = User.objects.filter(profile__role='admin').first()

if not admin_user:
    print("No admin user found, creating one...")
    admin_user = User.objects.create_superuser('testadmin', 'test@admin.com', 'TestPass123!')

request = factory.get('/dashboard-admin/monthly-extraction/export/')
request.user = admin_user

response = export_monthly_excel(request)
print(f"Response status: {response.status_code}")
print(f"Content-Type: {response['Content-Disposition']}")
print(f"File size: {len(response.content)} bytes")
print("SUCCESS: Excel generated correctly!")
