#!/usr/bin/env python
"""
Test script to verify validator edit/delete functionality
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from documents.models import Profile, Document, AuditLog

# Test setup
print("=" * 60)
print("VALIDATOR EDIT/DELETE FEATURE TEST")
print("=" * 60)

client = Client()

# Test 1: Verify test users exist
print("\n✅ TEST 1: Verify test users exist")
print("-" * 40)

try:
    diego = User.objects.get(username='diego')
    print(f"✓ Admin 'diego' found: {diego.email}")
    print(f"  Role: {diego.profile.role}")
except User.DoesNotExist:
    print("✗ Admin 'diego' not found!")
    sys.exit(1)

try:
    validador1 = User.objects.get(username='validador1')
    print(f"✓ Validator 'validador1' found: {validador1.email}")
    print(f"  Role: {validador1.profile.role}")
except User.DoesNotExist:
    print("✗ Validator 'validador1' not found!")
    sys.exit(1)

# Test 2: Login as admin
print("\n✅ TEST 2: Login as admin")
print("-" * 40)

login_success = client.login(username='diego', password='TestPassword123!')
if login_success:
    print("✓ Admin login successful")
else:
    print("✗ Admin login failed!")
    sys.exit(1)

# Test 3: Access admin dashboard
print("\n✅ TEST 3: Access admin dashboard")
print("-" * 40)

response = client.get('/dashboard-admin/')
if response.status_code == 200:
    print(f"✓ Dashboard accessed: status {response.status_code}")
    if 'validador1' in str(response.content):
        print("✓ Validator 'validador1' appears in dashboard")
    else:
        print("⚠ Warning: Validator 'validador1' not in dashboard content")
else:
    print(f"✗ Dashboard access failed: status {response.status_code}")
    sys.exit(1)

# Test 4: Test EDIT validator
print("\n✅ TEST 4: Edit validator information")
print("-" * 40)

# Get edit page
response = client.get(f'/dashboard-admin/validator/{validador1.id}/edit/')
if response.status_code == 200:
    print(f"✓ Edit page accessed: status {response.status_code}")
    if 'validador1' in str(response.content):
        print("✓ Edit form contains validator username")
else:
    print(f"✗ Edit page access failed: status {response.status_code}")

# Submit edit
edit_data = {
    'first_name': 'Juan',
    'last_name': 'Pérez',
    'email': 'juan.perez@test.com',
    'validator_type': 'validator1'
}
response = client.post(f'/dashboard-admin/validator/{validador1.id}/edit/', edit_data, follow=True)
if response.status_code == 200:
    print(f"✓ Edit submitted: status {response.status_code}")
    
    # Verify changes in database
    validador1_updated = User.objects.get(id=validador1.id)
    if validador1_updated.first_name == 'Juan':
        print(f"✓ First name updated: {validador1_updated.first_name}")
    else:
        print(f"✗ First name NOT updated: {validador1_updated.first_name}")
    
    if validador1_updated.email == 'juan.perez@test.com':
        print(f"✓ Email updated: {validador1_updated.email}")
    else:
        print(f"✗ Email NOT updated: {validador1_updated.email}")
    
    # Check audit log
    audit_entries = AuditLog.objects.filter(
        table_name='auth_user',
        row_pk=validador1.id,
        action='UPDATE'
    ).order_by('-changed_at')
    if audit_entries.exists():
        latest = audit_entries.first()
        print(f"✓ AuditLog entry created: {latest.action} by {latest.changed_by.username}")
    else:
        print("⚠ Warning: No AuditLog entry for edit")
else:
    print(f"✗ Edit submission failed: status {response.status_code}")

# Test 5: Test DELETE validator (non-validator1 to avoid conflicts)
print("\n✅ TEST 5: Delete validator")
print("-" * 40)

try:
    validador2 = User.objects.get(username='validador2')
    validator2_id = validador2.id
    
    # Get delete confirmation page
    response = client.get(f'/dashboard-admin/validator/{validator2_id}/delete/')
    if response.status_code == 200:
        print(f"✓ Delete confirmation page accessed: status {response.status_code}")
        if 'validador2' in str(response.content):
            print("✓ Delete page shows validator info")
    else:
        print(f"✗ Delete page access failed: status {response.status_code}")
    
    # Submit delete with confirmation
    delete_data = {'confirm': 'si'}
    response = client.post(f'/dashboard-admin/validator/{validator2_id}/delete/', delete_data, follow=True)
    if response.status_code == 200:
        print(f"✓ Delete submitted: status {response.status_code}")
        
        # Verify deletion
        try:
            User.objects.get(id=validator2_id)
            print("✗ Validator NOT deleted from database")
        except User.DoesNotExist:
            print("✓ Validator successfully deleted from database")
            
            # Check audit log
            audit_entries = AuditLog.objects.filter(
                table_name='auth_user',
                row_pk=validator2_id,
                action='DELETE'
            )
            if audit_entries.exists():
                print(f"✓ AuditLog DELETE entry created")
            else:
                print("⚠ Warning: No AuditLog DELETE entry")
    else:
        print(f"✗ Delete submission failed: status {response.status_code}")
        
except User.DoesNotExist:
    print("⚠ Validator 'validador2' not found - skipping delete test")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
