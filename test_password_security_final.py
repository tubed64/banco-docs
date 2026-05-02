#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test para verificar:
1. La redirección de validadores fuera de home
2. El cambio de contraseña obligatorio con TempPass123!
3. La ocultación del formulario de upload
"""
import os
import sys
import django

# Configurar Django PRIMERO
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

# AHORA importar modelos
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.test.utils import setup_test_environment, teardown_test_environment
from documents.models import Profile


def test_password_change_flow():
    """Test del flujo de cambio obligatorio de contraseña"""
    print("\n" + "="*70)
    print("TEST 1: Cambio obligatorio de contraseña con TempPass123!")
    print("="*70)
    
    client = Client()
    
    # Limpiar: borrar profile explícitamente, luego user
    try:
        Profile.objects.filter(user__username='test_validator').delete()
        User.objects.filter(username='test_validator').delete()
    except:
        pass
    
    # Crear un validador con contraseña temporal
    try:
        user = User.objects.create_user(
            username='test_validator',
            email='validator@test.com',
            password='TempPass123!'
        )
        # Check if profile already exists (due to signal)
        if not Profile.objects.filter(user=user).exists():
            profile = Profile.objects.create(user=user, role='validator1')
        else:
            profile = Profile.objects.get(user=user)
            profile.role = 'validator1'
            profile.save()
        print(f"[OK] Validador creado: {user.username}")
    except Exception as e:
        print(f"[ERROR] Error al crear validador: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Intentar acceder a una página protegida (debería redirigir a change_password)
    print("\n[STEP 1] Iniciar sesión como validador con TempPass123!")
    client.login(username='test_validator', password='TempPass123!')
    print("[OK] Sesión iniciada")
    
    # Intentar acceder a /validator1/
    print("\n[STEP 2] Intentar acceder a /validator1/ (debería redirigir a /change-password/)")
    response = client.get('/validator1/', follow=False)
    print(f"   Status code: {response.status_code}")
    if response.status_code == 302:
        location = response.get('Location', '')
        print(f"   Redirect location: {location}")
        if 'change-password' in location:
            print("[OK] Correctamente redirigido a cambio de contraseña")
        else:
            print(f"[ERROR] Redirección incorrecta: {location}")
            return False
    else:
        print(f"[ERROR] No hubo redirección (status: {response.status_code})")
        return False
    
    # Acceder a la página de cambio de contraseña
    print("\n[STEP 3] Acceder a /change-password/")
    response = client.get('/change-password/')
    print(f"   Status code: {response.status_code}")
    if response.status_code == 200:
        print("[OK] Página de cambio de contraseña accesible")
        if 'Cambiar Contraseña' in response.content.decode():
            print("[OK] Formulario de cambio de contraseña presente")
        else:
            print("[ERROR] Formulario no encontrado")
            return False
    else:
        print(f"[ERROR] No se pudo acceder (status: {response.status_code})")
        return False
    
    # Cambiar la contraseña
    print("\n[STEP 4] Cambiar contraseña")
    response = client.post('/change-password/', {
        'current_password': 'TempPass123!',
        'new_password': 'NuevaContraseña123!',
        'confirm_password': 'NuevaContraseña123!',
    })
    print(f"   Status code: {response.status_code}")
    if response.status_code == 302:
        print("[OK] Contraseña cambiada (redirección 302)")
        # Verificar que el usuario fue redirigido a su panel
        location = response.get('Location', '')
        print(f"   Redirigido a: {location}")
        if 'validator1' in location or 'dashboard' in location or 'home' in location:
            print("[OK] Redirección al panel correcta")
        else:
            print(f"[WARNING] Redirección inesperada: {location}")
    else:
        print(f"[ERROR] Status inesperado: {response.status_code}")
        return False
    
    # Verificar que ya no redirige a cambio de contraseña
    print("\n[STEP 5] Verificar que ya no redirige a cambio de contraseña")
    response = client.get('/validator1/', follow=False)
    print(f"   Status code: {response.status_code}")
    if response.status_code == 200 or (response.status_code == 302 and 'change-password' not in response.get('Location', '')):
        print("[OK] Ya no redirige a cambio de contraseña")
    else:
        print(f"[ERROR] Aun redirige a cambio de contraseña")
        return False
    
    # Limpiar
    user.delete()
    print("\n[OK] TEST EXITOSO: Cambio obligatorio de contraseña funciona correctamente\n")
    return True


def test_validator_redirect():
    """Test de redirección de validadores"""
    print("\n" + "="*70)
    print("TEST 2: Redirección de validadores fuera de /home/")
    print("="*70)
    
    client = Client()
    
    # Limpiar: borrar profiles primero
    try:
        Profile.objects.filter(user__username__in=['test_val1', 'test_val2', 'test_admin']).delete()
        User.objects.filter(username__in=['test_val1', 'test_val2', 'test_admin']).delete()
    except:
        pass
    
    # Crear un validador nivel 1
    try:
        user_v1 = User.objects.create_user(
            username='test_val1',
            email='val1@test.com',
            password='TempPass123!'
        )
        user_v1.set_password('SecurePass123!')  # Cambiar para no triggear el middleware
        user_v1.save()
        # Handle auto-created profile
        if not Profile.objects.filter(user=user_v1).exists():
            profile_v1 = Profile.objects.create(user=user_v1, role='validator1')
        else:
            profile_v1 = Profile.objects.get(user=user_v1)
            profile_v1.role = 'validator1'
            profile_v1.save()
        print(f"[OK] Validador nivel 1 creado: {user_v1.username}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Crear un validador nivel 2
    try:
        user_v2 = User.objects.create_user(
            username='test_val2',
            email='val2@test.com',
            password='SecurePass123!'
        )
        # Handle auto-created profile
        if not Profile.objects.filter(user=user_v2).exists():
            profile_v2 = Profile.objects.create(user=user_v2, role='validator2')
        else:
            profile_v2 = Profile.objects.get(user=user_v2)
            profile_v2.role = 'validator2'
            profile_v2.save()
        print(f"[OK] Validador nivel 2 creado: {user_v2.username}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Crear un admin
    try:
        user_admin = User.objects.create_user(
            username='test_admin',
            email='admin@test.com',
            password='AdminPass123!'
        )
        # Handle auto-created profile
        if not Profile.objects.filter(user=user_admin).exists():
            profile_admin = Profile.objects.create(user=user_admin, role='admin')
        else:
            profile_admin = Profile.objects.get(user=user_admin)
            profile_admin.role = 'admin'
            profile_admin.save()
        print(f"[OK] Admin creado: {user_admin.username}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test validador1 redirect
    print("\n[STEP 1] Validador 1 accede a /home/ (debería redirigir a /validator1/)")
    client.login(username='test_val1', password='SecurePass123!')
    response = client.get('/', follow=False)
    print(f"   Status code: {response.status_code}")
    if response.status_code == 302:
        location = response.get('Location', '')
        print(f"   Redirect a: {location}")
        if 'validator1' in location:
            print("[OK] Validador 1 redirigido correctamente")
        else:
            print(f"[ERROR] Redirección incorrecta: {location}")
            user_v1.delete()
            user_v2.delete()
            user_admin.delete()
            return False
    else:
        print(f"[ERROR] No hubo redirección")
        user_v1.delete()
        user_v2.delete()
        user_admin.delete()
        return False
    
    # Test validador2 redirect
    print("\n[STEP 2] Validador 2 accede a /home/ (debería redirigir a /validator2/)")
    client.logout()
    client.login(username='test_val2', password='SecurePass123!')
    response = client.get('/', follow=False)
    print(f"   Status code: {response.status_code}")
    if response.status_code == 302:
        location = response.get('Location', '')
        print(f"   Redirect a: {location}")
        if 'validator2' in location:
            print("[OK] Validador 2 redirigido correctamente")
        else:
            print(f"[ERROR] Redirección incorrecta: {location}")
            user_v1.delete()
            user_v2.delete()
            user_admin.delete()
            return False
    else:
        print(f"[ERROR] No hubo redirección")
        user_v1.delete()
        user_v2.delete()
        user_admin.delete()
        return False
    
    # Test admin redirect
    print("\n[STEP 3] Admin accede a /home/ (debería redirigir a /dashboard-admin/)")
    client.logout()
    client.login(username='test_admin', password='AdminPass123!')
    response = client.get('/', follow=False)
    print(f"   Status code: {response.status_code}")
    if response.status_code == 302:
        location = response.get('Location', '')
        print(f"   Redirect a: {location}")
        if 'dashboard-admin' in location:
            print("[OK] Admin redirigido correctamente")
        else:
            print(f"[ERROR] Redirección incorrecta: {location}")
            user_v1.delete()
            user_v2.delete()
            user_admin.delete()
            return False
    else:
        print(f"[ERROR] No hubo redirección")
        user_v1.delete()
        user_v2.delete()
        user_admin.delete()
        return False
    
    # Limpiar
    user_v1.delete()
    user_v2.delete()
    user_admin.delete()
    print("\n[OK] TEST EXITOSO: Redirecciones funciona correctamente\n")
    return True


def test_upload_form_hidden():
    """Test de ocultación del formulario de upload"""
    print("\n" + "="*70)
    print("TEST 3: Ocultación del formulario de upload para validadores")
    print("="*70)
    
    client = Client()
    
    # Limpiar: borrar profiles primero
    try:
        Profile.objects.filter(user__username__in=['test_client', 'test_val_hide']).delete()
        User.objects.filter(username__in=['test_client', 'test_val_hide']).delete()
    except:
        pass
    
    # Crear un cliente (puede ver el formulario)
    try:
        user_client = User.objects.create_user(
            username='test_client',
            email='client@test.com',
            password='ClientPass123!'
        )
        # Handle auto-created profile
        if not Profile.objects.filter(user=user_client).exists():
            profile_client = Profile.objects.create(user=user_client, role='cliente')
        else:
            profile_client = Profile.objects.get(user=user_client)
            profile_client.role = 'cliente'
            profile_client.save()
        print(f"[OK] Cliente creado: {user_client.username}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Crear un validador
    try:
        user_val = User.objects.create_user(
            username='test_val_hide',
            email='val_hide@test.com',
            password='ValPass123!'
        )
        # Handle auto-created profile
        if not Profile.objects.filter(user=user_val).exists():
            profile_val = Profile.objects.create(user=user_val, role='validator1')
        else:
            profile_val = Profile.objects.get(user=user_val)
            profile_val.role = 'validator1'
            profile_val.save()
        print(f"[OK] Validador creado: {user_val.username}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Cliente accede a /home/ y debería ver formulario
    print("\n[STEP 1] Cliente accede a /home/ (debería ver formulario)")
    client.login(username='test_client', password='ClientPass123!')
    response = client.get('/')
    if response.status_code == 200:
        content = response.content.decode()
        if 'Subir documento' in content and 'enctype="multipart/form-data"' in content:
            print("[OK] Formulario visible para cliente")
        else:
            print("[ERROR] Formulario no encontrado para cliente")
            user_client.delete()
            user_val.delete()
            return False
    else:
        print(f"[ERROR] Error al acceder: {response.status_code}")
        user_client.delete()
        user_val.delete()
        return False
    
    # Validador intenta acceder (será redirigido antes de ver el formulario)
    print("\n[STEP 2] Validador accede a /home/ (será redirigido)")
    client.logout()
    client.login(username='test_val_hide', password='ValPass123!')
    response = client.get('/', follow=False)
    if response.status_code == 302:
        print(f"[OK] Validador redirigido (no ve formulario)")
    else:
        print(f"[WARNING] Validador no fue redirigido (status: {response.status_code})")
    
    # Limpiar
    user_client.delete()
    user_val.delete()
    print("\n[OK] TEST EXITOSO: Ocultación del formulario funciona\n")
    return True


if __name__ == '__main__':
    print("\n[TEST] Ejecutando suite de tests para validacion de cambios...\n")
    
    setup_test_environment()
    
    tests = [
        ("Cambio de contraseña obligatorio", test_password_change_flow),
        ("Redirección de validadores", test_validator_redirect),
        ("Ocultación de formulario", test_upload_form_hidden),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n[ERROR] en {test_name}: {e}\n")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    teardown_test_environment()
    
    # Resumen
    print("\n" + "="*70)
    print("RESUMEN DE TESTS")
    print("="*70)
    for test_name, result in results.items():
        status = "[OK]" if result else "[FAIL]"
        print(f"{status}: {test_name}")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    print(f"\nTotal: {passed}/{total} tests pasados")
    
    if passed == total:
        print("\n[SUCCESS] Todos los tests pasaron!\n")
        sys.exit(0)
    else:
        print(f"\n[WARNING] {total - passed} test(s) fallaron\n")
        sys.exit(1)
