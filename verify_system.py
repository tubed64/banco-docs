#!/usr/bin/env python
"""Quick system verification"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path.cwd()
load_dotenv(BASE_DIR / '.env')

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

client = Client()

# Test login and access admin dashboard
print('Testing admin panel access...')
success = client.login(username='diego', password='TestPassword123!')
print(f'Login: {"✅ Success" if success else "❌ Failed"}')

response = client.get('/dashboard-admin/')
print(f'Admin panel: {response.status_code} (expect 200)')

# Check validators in database
validators = User.objects.filter(profile__role__in=['validator1', 'validator2'])
print(f'\nValidators in system: {validators.count()}')
for v in validators:
    print(f'  - {v.username}: {v.first_name} {v.last_name} ({v.email})')

print('\n✅ System verification complete')
