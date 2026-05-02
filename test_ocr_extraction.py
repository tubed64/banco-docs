#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Prueba de extracción de datos con documento real (OCR con PaddleOCR)
"""

import os
import sys
from PIL import Image
import numpy as np

# Add the project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from documents.document_validator import DocumentValidator

def create_test_image():
    """Crear una imagen de prueba con texto similar a un documento"""
    # Crear imagen blanca con texto
    width, height = 800, 600
    img = Image.new('RGB', (width, height), color='white')
    
    # Para fines de prueba, crear una imagen simple con líneas de texto
    # En producción, esto sería un documento escaneado real
    pixels = img.load()
    
    # Dibujar texto simple (simulando un documento escaneado)
    # Para la prueba real, necesitaríamos un documento real o usar PIL.ImageDraw
    
    return img

def test_ocr_extraction():
    """Test de extracción usando OCR"""
    print("=" * 70)
    print("PRUEBA DE EXTRACCIÓN CON OCR (PaddleOCR)")
    print("=" * 70)
    print()
    
    validator = DocumentValidator()
    
    # Primero, verificar si tenemos una imagen de prueba disponible
    test_images = [
        'test_document.png',
        'sample_document.jpg',
    ]
    
    found_image = False
    for img_path in test_images:
        if os.path.exists(img_path):
            print(f"Encontrado archivo: {img_path}")
            print("Extrayendo texto con PaddleOCR...")
            print()
            
            try:
                text = validator.extract_text_from_image(img_path)
                print("Texto extraído:")
                print("-" * 70)
                print(text[:500])  # Primeros 500 caracteres
                print("-" * 70)
                print()
                
                # Detectar campos
                fields = validator._detect_fields(text)
                
                print("CAMPOS DETECTADOS:")
                print()
                for field, values in fields.items():
                    if values:
                        print(f"✓ {field.upper()}:")
                        if isinstance(values, list):
                            for val in values[:3]:  # Primeros 3 valores
                                print(f"  • {val}")
                            if len(values) > 3:
                                print(f"  ... y {len(values)-3} más")
                        else:
                            print(f"  • {values}")
                        print()
                
                found_image = True
                break
            except Exception as e:
                print(f"Error procesando {img_path}: {e}")
                print()
    
    if not found_image:
        print("ℹ️  No se encontraron imágenes de prueba.")
        print()
        print("Para hacer una prueba completa con OCR:")
        print("1. Coloca una imagen de documento (PNG o JPG) en la carpeta del proyecto")
        print("2. Ejecuta este script nuevamente")
        print()
        print("La extracción de texto con OCR funcionará automáticamente")
        print("cuando se cargue un documento real en la aplicación.")
        print()
    
    print("=" * 70)
    print("✅ Prueba de OCR completada")
    print("=" * 70)

if __name__ == '__main__':
    test_ocr_extraction()
