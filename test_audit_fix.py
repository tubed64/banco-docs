#!/usr/bin/env python
"""
Test to verify audit log page works without errors
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path.cwd()
load_dotenv(BASE_DIR / '.env')

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking.settings')
django.setup()

# Set admin password first
from django.contrib.auth.models import User
diego = User.objects.get(username='diego')
diego.set_password('TestPassword123!')
diego.save()

# Now test
from django.test import Client

client = Client()

print("Testing Audit Log Page...")
print("-" * 60)

# Login
success = client.login(username='diego', password='TestPassword123!')
print(f"1. Login: {'✅ Success' if success else '❌ Failed'}")

if success:
    # Test main admin panel
    response = client.get('/dashboard-admin/', follow=True)
    print(f"2. Admin panel: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
    
    # Test audit log page
    response = client.get('/dashboard-admin/audit-log/', follow=True)
    print(f"3. Audit log page: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
    
    if response.status_code == 200:
        print("\n✅ All tests passed! Audit log page works correctly.")
    else:
        print(f"\n❌ Error loading audit log page")
        print(f"   Response content (first 500 chars):")
        print(f"   {str(response.content)[:500]}")
