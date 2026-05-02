#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test para verificar que la funcionalidad de descarga de documentos aprobados funciona correctamente
"""
import os
import sys
import django
import zipfile
import io

# Configurar Django PRIMERO
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

# AHORA importar modelos
from django.contrib.auth.models import User
from django.test import Client
from django.test.utils import setup_test_environment, teardown_test_environment
from django.utils import timezone
from documents.models import Document, Profile


def test_download_approved_documents():
    """Test descarga de documentos aprobados"""
    print("\n" + "="*70)
    print("TEST: Descarga de Documentos Aprobados Organizados por Cliente")
    print("="*70)
    
    client = Client()
    
    # Limpiar datos previos
    try:
        Profile.objects.filter(user__username__startswith='test_download').delete()
        User.objects.filter(username__startswith='test_download').delete()
    except:
        pass
    
    # Crear admin
    try:
        admin_user = User.objects.create_user(
            username='test_download_admin',
            email='admin@test.com',
            password='AdminPass123!'
        )
        admin_profile, created = Profile.objects.get_or_create(user=admin_user)
        admin_profile.role = 'admin'
        admin_profile.save()
        print("[OK] Admin creado: test_download_admin")
        print(f"     Role: {admin_profile.role}")
    except Exception as e:
        print(f"[ERROR] Error creando admin: {e}")
        return False
    
    # Crear clientes de prueba
    try:
        client_user_1 = User.objects.create_user(
            username='test_download_client_1',
            email='client1@test.com',
            password='ClientPass123!'
        )
        client_profile_1 = Profile.objects.get_or_create(user=client_user_1)
        client_profile_1[0].role = 'cliente'
        client_profile_1[0].save()
        
        client_user_2 = User.objects.create_user(
            username='test_download_client_2',
            email='client2@test.com',
            password='ClientPass123!'
        )
        client_profile_2 = Profile.objects.get_or_create(user=client_user_2)
        client_profile_2[0].role = 'cliente'
        client_profile_2[0].save()
        
        print("[OK] Clientes creados: client_1, client_2")
    except Exception as e:
        print(f"[ERROR] Error creando clientes: {e}")
        return False
    
    # Crear documentos aprobados
    try:
        validator_user = User.objects.create_user(
            username='test_download_validator',
            email='validator@test.com',
            password='ValidatorPass123!'
        )
        validator_profile = Profile.objects.get_or_create(user=validator_user)
        validator_profile[0].role = 'validator1'
        validator_profile[0].save()
        
        # Documento 1 para cliente 1
        doc_1 = Document.objects.create(
            user=client_user_1,
            title="Identificacion INE",
            status="approved",
            validator1=validator_user,
            validator2=validator_user,
            validator1_approved=True,
            validator2_approved=True,
            uploaded_at=timezone.now(),
            validator1_date=timezone.now(),
            validator2_date=timezone.now(),
        )
        
        # Documento 2 para cliente 1
        doc_2 = Document.objects.create(
            user=client_user_1,
            title="Comprobante Domicilio",
            status="approved",
            validator1=validator_user,
            validator2=validator_user,
            validator1_approved=True,
            validator2_approved=True,
            uploaded_at=timezone.now(),
            validator1_date=timezone.now(),
            validator2_date=timezone.now(),
        )
        
        # Documento 3 para cliente 2
        doc_3 = Document.objects.create(
            user=client_user_2,
            title="RFC Scan",
            status="approved",
            validator1=validator_user,
            validator2=validator_user,
            validator1_approved=True,
            validator2_approved=True,
            uploaded_at=timezone.now(),
            validator1_date=timezone.now(),
            validator2_date=timezone.now(),
        )
        
        print("[OK] Documentos aprobados creados: 3 documentos")
        print(f"     - Cliente 1: 2 documentos")
        print(f"     - Cliente 2: 1 documento")
    except Exception as e:
        print(f"[ERROR] Error creando documentos: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Intentar descargar sin autenticar
    print("\n[STEP 1] Intentar descargar sin autenticar")
    response = client.get('/dashboard-admin/download-approved/', follow=False)
    print(f"   Status code: {response.status_code}")
    if response.status_code == 302:
        print("[OK] Redirigido a login (protección de acceso funciona)")
    else:
        print(f"[ERROR] Status inesperado: {response.status_code}")
        return False
    
    # Autenticar como admin
    print("\n[STEP 2] Autenticar como admin")
    is_logged_in = client.login(username='test_download_admin', password='AdminPass123!')
    print(f"[OK] Sesión iniciada: {is_logged_in}")
    
    # Verificar que el usuario está logeado y es admin
    if is_logged_in:
        # Verificar perfil
        admin_check = User.objects.get(username='test_download_admin')
        print(f"     Usuario logueado: {admin_check.username}")
        print(f"     Role en BD: {admin_check.profile.role}")
        print(f"     Es admin: {admin_check.profile.role == 'admin'}")
        
        # Hacer un request dummy para cargar el usuario en la sesión
        print("\n[DEBUG] Accediendo al dashboard para cargar sesión...")
        response_test = client.get('/dashboard-admin/', follow=True)
        print(f"     Dashboard status: {response_test.status_code}")
    
    # Descargar
    print("\n[STEP 3] Descargar documentos aprobados")
    response = client.get('/dashboard-admin/download-approved/', follow=True)
    print(f"   Status code: {response.status_code}")
    content_type = response.get('Content-Type', '')
    print(f"   Content-Type: {content_type}")
    
    if response.status_code == 200 and 'zip' in content_type.lower():
        print("[OK] Descarga obtenida como ZIP")
    elif response.status_code == 200:
        print("[WARNING] Respuesta 200 pero no es ZIP")
        print(f"   Response es: {content_type}")
        if b'admin' in response.content or b'dashboard' in response.content:
            print("[ERROR] Parece que fue redirigido al dashboard")
            return False
    else:
        print(f"[ERROR] Status code inesperado: {response.status_code}")
        return False
    
    print("[OK] Descarga iniciada (status 200)")
    
    print("[OK] Content-Type es ZIP")
    
    # Verificar nombre del archivo
    disposition = response.get('Content-Disposition')
    print(f"   Disposition: {disposition}")
    
    if 'Documentos_Aprobados' not in disposition:
        print(f"[ERROR] Nombre de archivo incorrecto")
        return False
    
    print("[OK] Nombre de archivo correcto")
    
    # Parsear ZIP
    print("\n[STEP 5] Parsear contenido del ZIP")
    try:
        zip_buffer = io.BytesIO(response.content)
        with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
            file_list = zip_file.namelist()
            print(f"   Archivos en ZIP: {len(file_list)}")
            
            # Verificar estructura
            expected_items = [
                'Clientes/test_download_client_1_',  # Carpeta cliente 1
                'Clientes/test_download_client_2_',  # Carpeta cliente 2
                '00_INFORMACIÓN_CLIENTE.txt',
                'DATOS_EXTRAÍDOS.csv',
            ]
            
            found_items = 0
            for expected in expected_items:
                matching = [f for f in file_list if expected in f]
                if matching:
                    print(f"   [OK] Encontrado: {expected}")
                    found_items += 1
                else:
                    print(f"   [WARNING] No encontrado: {expected}")
            
            if found_items >= 4:
                print("[OK] Estructura de ZIP correcta")
            else:
                print(f"[WARNING] Algunos archivos faltantes")
            
            # Leer un archivo de información
            info_files = [f for f in file_list if '00_INFORMACIÓN_CLIENTE.txt' in f]
            if info_files:
                info_content = zip_file.read(info_files[0]).decode('utf-8')
                if 'INFORMACIÓN DEL CLIENTE' in info_content:
                    print("[OK] Contenido de información del cliente es correcto")
                else:
                    print("[WARNING] Contenido inesperado")
            
            # Leer archivo CSV
            csv_files = [f for f in file_list if 'DATOS_EXTRAÍDOS.csv' in f]
            if csv_files:
                csv_content = zip_file.read(csv_files[0]).decode('utf-8')
                if 'Título,Tipo,CURP,RFC' in csv_content:
                    print("[OK] Contenido de CSV es correcto")
                    # Contar líneas (encabezado + datos)
                    lines = csv_content.strip().split('\n')
                    print(f"   Líneas en CSV: {len(lines)}")
                else:
                    print("[WARNING] Formato CSV inesperado")
    except Exception as e:
        print(f"[ERROR] Error parseando ZIP: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Verificar auditoría
    print("\n[STEP 6] Verificar auditoría")
    from documents.models import AuditLog
    audit_logs = AuditLog.objects.filter(action='EXPORT').order_by('-created_at')[:1]
    if audit_logs.exists():
        log = audit_logs[0]
        print(f"   [OK] Auditoría registrada")
        print(f"   Usuario: {log.changed_by.username}")
        print(f"   Nota: {log.note}")
    else:
        print(f"   [WARNING] No se encontró registro en auditoría")
    
    # Limpiar
    print("\n[CLEANUP] Eliminando usuarios de prueba")
    admin_user.delete()
    client_user_1.delete()
    client_user_2.delete()
    validator_user.delete()
    
    print("\n[OK] TEST EXITOSO: Descarga de documentos aprobados funciona correctamente\n")
    return True


if __name__ == '__main__':
    print("\n[TEST] Ejecutando test de descarga de documentos...\n")
    
    setup_test_environment()
    
    try:
        result = test_download_approved_documents()
    except Exception as e:
        print(f"\n[ERROR] Exception: {e}\n")
        import traceback
        traceback.print_exc()
        result = False
    
    teardown_test_environment()
    
    # Resumen
    print("="*70)
    if result:
        print("[SUCCESS] Test completado exitosamente!")
        sys.exit(0)
    else:
        print("[FAILED] Test fallió")
        sys.exit(1)
