#!/usr/bin/env python
"""
Test para demostrar la extracción de datos mejorada del documento_validator
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path.cwd()
load_dotenv(BASE_DIR / '.env')

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking.settings')
django.setup()

from documents.document_validator import DocumentValidator

# Ejemplo de texto que podría extraer OCR de un documento
test_text_examples = [
    # Ejemplo 1: Comprobante de domicilio
    """
    COMPROBANTE DE DOMICILIO
    
    Nombre: Juan Carlos Pérez García
    CURP: PEGJ 850415 H DFN RN 09
    RFC: PEGJ850415FG9
    
    Domicilio: Avenida Paseo de la Reforma 505, Apartado 1205
    Delegación: Cuauhtémoc
    Estado: Ciudad de México
    Código Postal: 06500
    
    Teléfono: 55-2345-6789
    Email: juan.perez@email.com
    
    Ocupación: Ingeniero
    Estado Civil: Casado
    
    Fecha de expedición: 15/04/2025
    """,
    
    # Ejemplo 2: Identificación  
    """
    CREDENCIAL PARA VOTAR
    NOMBRE: MARÍA GARCÍA SÁNCHEZ
    CURP: GASM 900820 H DFR RL 08
    RFC: GASM900820FH2
    
    DOMICILIO: Calle Benito Juárez número 123, Departamento 4
    Ciudad: Guadalajara
    Estado: Jalisco
    CP: 44100
    
    TELÉFONO CELULAR: +52-331-234-5678
    CORREO: maria.garcia@correo.com
    
    PROFESIÓN: Contadora Pública
    ESTADO CIVIL: Soltera
    FECHA NACIMIENTO: 20/08/1990
    VÁLIDO HASTA: 15/04/2030
    """,
    
    # Ejemplo 3: Documento de banco
    """
    SOLICITUD DE CRÉDITO
    
    Solicitante: Roberto Martínez López
    CURP: MALR 800310 H DFR BB 03
    RFC: MALR800310HL3
    
    Domicilio actual: Carrera 15 número 45-67, Apartado 308
    Municipio: Monterrey
    Estado: Nuevo León
    
    Teléfono de contacto: 81-8765-4321
    Email personal: r.martinez@email.mx
    
    Ocupación: Gerente Comercial
    Estado civil: Casado
    Fecha de nacimiento: 10/03/1980
    """
]

print("=" * 70)
print("PRUEBA DE EXTRACCIÓN MEJORADA DE DATOS")
print("=" * 70)

validator = DocumentValidator()

for idx, test_text in enumerate(test_text_examples, 1):
    print(f"\n{'='*70}")
    print(f"EJEMPLO {idx}")
    print(f"{'='*70}")
    
    # Detecta campos
    fields = validator._detect_fields(test_text)
    
    print("\n📋 DATOS EXTRAÍDOS:\n")
    
    print(f"🆔 CURP:")
    if fields['curp']:
        for curp in fields['curp']:
            print(f"   • {curp}")
    else:
        print("   ❌ No detectado")
    
    print(f"\n🏛️  RFC:")
    if fields['rfc']:
        for rfc in fields['rfc']:
            print(f"   • {rfc}")
    else:
        print("   ❌ No detectado")
    
    print(f"\n👤 NOMBRES:")
    if fields['names']:
        for name in fields['names']:
            print(f"   • {name}")
    else:
        print("   ❌ No detectado")
    
    print(f"\n🏘️  DOMICILIO:")
    if fields['addresses']:
        for addr in fields['addresses']:
            print(f"   • {addr}")
    else:
        print("   ❌ No detectado")
    
    print(f"\n📞 TELÉFONO:")
    if fields['phone']:
        for phone in fields['phone']:
            print(f"   • {phone}")
    else:
        print("   ❌ No detectado")
    
    print(f"\n📧 EMAIL:")
    if fields['email']:
        for email in fields['email']:
            print(f"   • {email}")
    else:
        print("   ❌ No detectado")
    
    print(f"\n📅 FECHAS:")
    if fields['dates']:
        for date in fields['dates']:
            print(f"   • {date}")
    else:
        print("   ❌ No detectado")
    
    print(f"\n💼 OCUPACIÓN:")
    if fields['ocupation']:
        for occ in fields['ocupation']:
            print(f"   • {occ}")
    else:
        print("   ❌ No detectado")
    
    print(f"\n💑 ESTADO CIVIL:")
    if fields['marital_status']:
        for status in fields['marital_status']:
            print(f"   • {status}")
    else:
        print("   ❌ No detectado")
    
    print(f"\n🔢 NÚMEROS:")
    if fields['numbers']:
        for num in fields['numbers'][:5]:  # Mostrar solo los primeros 5
            print(f"   • {num}")
        if len(fields['numbers']) > 5:
            print(f"   ... y {len(fields['numbers']) - 5} más")
    else:
        print("   ❌ No detectado")

print("\n" + "=" * 70)
print("✅ PRUEBA COMPLETADA")
print("=" * 70)
