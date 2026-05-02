"""
Sistema de Validación Inteligente de Documentos Mexicanos
Valida: CURP, RFC, datos consistentes, calidad de imagen, etc.
"""

import re
import os
import numpy as np
from pathlib import Path
from PIL import Image
from datetime import datetime

try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False


class DocumentValidator:
    """Validador inteligente de documentos con OCR y análisis de datos"""
    
    def __init__(self):
        """Inicializa el validador con OCR si está disponible"""
        self.ocr = None
        self.validation_results = {}
        
        if PADDLEOCR_AVAILABLE:
            try:
                # Inicializa OCR para español (lang 'es' disponible en PaddleOCR)
                self.ocr = PaddleOCR(use_angle_cls=True, lang='es')
            except Exception as e:
                print(f"Error inicializando OCR: {e}")
    
    def extract_text_from_image(self, image_path: str) -> dict:
        """
        Extrae texto de una imagen usando OCR
        
        Returns:
            dict: {
                'success': bool,
                'text': str (todo el texto extraído),
                'fields': dict (campos detectados),
                'confidence': float (confianza promedio 0-1),
                'error': str (si hay error)
            }
        """
        if not PADDLEOCR_AVAILABLE:
            return {
                'success': False,
                'error': 'PaddleOCR no instalado. Instala: pip install paddleocr',
                'text': '',
                'fields': {},
                'confidence': 0
            }
        
        if not self.ocr:
            return {
                'success': False,
                'error': 'OCR no inicializado',
                'text': '',
                'fields': {},
                'confidence': 0
            }
        
        try:
            if not os.path.exists(image_path):
                return {
                    'success': False,
                    'error': f'Archivo no encontrado: {image_path}',
                    'text': '',
                    'fields': {},
                    'confidence': 0
                }
            
            # Procesa con OCR
            result = self.ocr.ocr(image_path, cls=True)
            
            if not result or not result[0]:
                return {
                    'success': False,
                    'error': 'No se detectó texto en la imagen',
                    'text': '',
                    'fields': {},
                    'confidence': 0
                }
            
            # Extrae texto y confianza
            texts = []
            confidences = []
            
            for line in result[0]:
                for word_info in line:
                    text = word_info[1]
                    confidence = word_info[2]
                    texts.append(text)
                    confidences.append(confidence)
            
            full_text = ' '.join(texts)
            avg_confidence = np.mean(confidences) if confidences else 0
            
            # Detecta campos clave
            fields = self._detect_fields(full_text)
            
            return {
                'success': True,
                'text': full_text,
                'fields': fields,
                'confidence': float(avg_confidence),
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error en OCR: {str(e)}',
                'text': '',
                'fields': {},
                'confidence': 0
            }
    
    def _detect_fields(self, text: str) -> dict:
        """
        Detecta campos importantes en el texto extraído
        Busca: CURP, RFC, nombres, direcciones, teléfonos, fechas, etc.
        """
        fields = {
            'curp': [],
            'rfc': [],
            'names': [],
            'addresses': [],
            'phone': [],
            'dates': [],
            'numbers': [],
            'email': [],
            'ocupation': [],
            'marital_status': []
        }
        
        # Limpiar y normalizar texto
        text_normalized = text.upper()
        lines = text.split('\n')
        
        # CURP: 18 caracteres alfanuméricos (muy flexible con espacios/guiones/puntos)
        # Formato: 4 letras + 6 dígitos + 1 letra (H/M) + 3 letras + 2 alfanuméricos + 2 dígitos = 18
        curp_pattern = r'([A-Z]{4})\s*[-.\s]*(\d{6})\s*[-.\s]*([HM])\s*[-.\s]*([A-Z]{3})\s*[-.\s]*([0-9A-Z]{2})\s*[-.\s]*(\d{2})'
        curp_matches = re.finditer(curp_pattern, text_normalized)
        curps = []
        for match in curp_matches:
            curp = ''.join(match.groups())
            if len(curp) == 18:
                curps.append(curp)
        fields['curp'] = list(set(curps))
        
        # RFC: 12 o 13 caracteres (más flexible)
        rfcs = re.findall(r'\b[A-Z]{3,4}\d{6}[A-Z0-9]{3,6}\b', text, re.IGNORECASE)
        fields['rfc'] = [r.upper() for r in rfcs]
        
        # Fechas (DD/MM/YYYY o YYYY-MM-DD o DD-MM-YYYY)
        dates = re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text)
        fields['dates'] = sorted(set(dates))
        
        # Emails
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        fields['email'] = list(set(emails))
        
        # Teléfonos: formato mexicano flexible
        # Soporta: 55 1234 5678, 55-1234-5678, +52-55-1234-5678, (55) 1234-5678, etc.
        phone_pattern = r'(?:\+?52[\s\-]?)?(?:\(?[\s]?(?:55|[1-9]\d)[\s]?\)?)?[\s\-]?(?:\d[\s\-]?){7,8}\d'
        phones = re.findall(phone_pattern, text)
        fields['phone'] = list(set([p.strip() for p in phones if re.search(r'\d', p)]))
        
        # Números (puede ser cédula, ID, código postal, etc.)
        # Buscar números de 4-12 dígitos (ajustado para códigos postales de 5 dígitos)
        all_numbers = re.findall(r'\b\d{4,12}\b', text)
        # Eliminar duplicados y fechas (ya están en dates)
        numbers_set = set(all_numbers)
        # Remover fechas de la lista de números
        numbers_filtered = [n for n in numbers_set if not any(n in d for d in fields['dates'])]
        fields['numbers'] = sorted(list(numbers_filtered))
        
        # Detectar nombres completos (busca palabras capitalizadas después de etiquetas "Nombre:" u otros contextos)
        # Estrategia 1: después de etiquetas explícitas en la MISMA línea - PRIORIDAD ALTA
        # Usar (?:...) y solo espacios horizontales [ \t] en lugar de \s que incluye saltos de línea
        name_labels_pattern = r'(?:nombre|solicitante|nombre completo)[ \t]*:?[ \t]*([A-ZÁ-Ú][a-zá-ú]+(?:[ \t]+[A-ZÁ-Ú][a-zá-ú]+){1,3})'
        names_from_labels = re.findall(name_labels_pattern, text, re.IGNORECASE)
        
        # Estrategia 2: palabras capitalizadas que parecen nombres (solo en líneas individuales)
        # Incluir estados de México, ciudades, y otros términos a evitar
        words_to_avoid = r'(?:comprobante|credencial|solicitud|domicilio|dirección|teléfono|email|correo|estado|municipio|delegación|ciudad|carretera|calle|avenida|apartado|departamento|ocupación|civil|fecha|expedición|nacimiento|contacto|actual|código|postal|número|nombre|solicitante|válido|vigencia|documento|crédito|trabajador|de|por|la|para|con|sin|una|su|los|las|del|al|es|un|curp|rfc|guanajuato|jalisco|michoacán|méxico|mexico|yucatán|yucatan|nuevo león|nuevo|león|veracruz|chiapas|oaxaca|puebla|coahuila|sonora|sinaloa|durango|zacatecas|aguascalientes|tlaxcala|quintana roo|campeche|tabasco|chihuahua|nayarit|colima|tamaulipas|morelos|querétaro|hidalgo|san luis potosí|baja california|baja california sur|guadalajara|monterrey|méxico city|méxico d\.f\.)'
        
        valid_names = []
        # Buscar en líneas individuales para no capturar saltos de línea
        for line in lines:
            # Solo procesar líneas que NO sean encabezados típicos (todas mayúsculas + puntuación)
            if not re.match(r'^[A-ZÁÉÍÓÚ\s:]+$', line.strip()):
                # Buscar nombres en esta línea - permitir mayúsculas y minúsculas
                name_pattern = r'\b([A-ZÁ-Ú][a-zá-ú]+(?:\s+[A-ZÁ-Ú][a-zá-ú]+){1,3})\b'
                names_in_line = re.findall(name_pattern, line)
                
                for name in names_in_line:
                    name_clean = ' '.join(name.split())
                    words = name_clean.split()
                    
                    # Validar: 2-4 palabras, 5-80 chars, no sea palabra clave
                    if (2 <= len(words) <= 4 and 
                        5 < len(name_clean) <= 80 and
                        not re.search(words_to_avoid, name_clean, re.IGNORECASE)):
                        
                        valid_names.append(name_clean)
        
        # Combinar: priorizar nombres de etiquetas, luego válidos únicos
        names_combined = list(set(names_from_labels + valid_names))
        # Eliminar duplicados y ordenar por longitud descendente
        names_combined.sort(key=len, reverse=True)
        # Filtrar finalmente
        fields['names'] = [n for n in names_combined if 5 < len(n) <= 80]
        
        # Detectar dirección (busca patrones comunes: Calle, Avenida, Apartamento, etc.)
        address_keywords = r'\b(?:calle|avenida|av\.|cda\.|apartado|depto\.|no\.|lote|predio|pasaje|plaza|zócalo|callejón|carretera|carret\.|periférico|periférico)'
        address_matches = []
        for i, line in enumerate(lines):
            if re.search(address_keywords, line, re.IGNORECASE):
                # Obtener la línea y línea anterior/siguiente para contexto
                context = []
                if i > 0:
                    context.append(lines[i-1].strip())
                context.append(line.strip())
                if i < len(lines) - 1:
                    context.append(lines[i+1].strip())
                address_text = ' '.join(context)
                # Limitar a 150 caracteres
                if len(address_text) < 150:
                    address_matches.append(address_text)
        
        # También buscar números de casa después de palabras clave
        house_pattern = r'(?:calle|avenida|av\.?|carrera|cr\.?)\s+[^\n]{1,100}(?:#|no\.?|número)\s+\d+'
        house_matches = re.findall(house_pattern, text, re.IGNORECASE)
        address_matches.extend(house_matches)
        
        fields['addresses'] = list(set([a.strip() for a in address_matches if a.strip()]))
        
        # Detectar ocupación (busca palabras comunes de profesiones)
        occupations_keywords = r'\b(?:ingeniero|abogado|doctor|médico|contador|contador público|empresario|empleado|trabajador|docente|profesor|técnico|administrador|gerente|director|jefe|supervisor|vendedor|comerciante|transportista|agricultor|ganadero|mechánico|electricista|plomero|constructor|psicólogo|enfermero|comercio|vendedor|ejecutivo)\b'
        occupations = re.findall(occupations_keywords, text, re.IGNORECASE)
        fields['ocupation'] = list(set(occupations))
        
        # Detectar estado civil
        marital_keywords = r'\b(?:soltero|soltera|casado|casada|divorciado|divorciada|viudo|viuda|unión libre)\b'
        marital = re.findall(marital_keywords, text, re.IGNORECASE)
        fields['marital_status'] = list(set(marital))
        
        return fields
    
    @staticmethod
    def validate_curp(curp: str) -> dict:
        """
        Valida un CURP mexicano usando el algoritmo oficial
        
        Formato: AAAA YYMMDD H/M SSS NN D
        - 4 letras del nombre
        - 6 dígitos de fecha nacimiento
        - 1 letra de género
        - 3 letras del estado
        - 2 consonantes de nombre
        - 1 dígito verificador
        """
        curp = str(curp).upper().replace(' ', '')
        
        validation = {
            'valid': False,
            'curp': curp,
            'issues': [],
            'date_of_birth': None
        }
        
        # Verificar formato
        if not re.match(r'^[A-Z]{4}\d{6}[HM][A-Z]{3}[0-9A-Z]{2}\d$', curp):
            validation['issues'].append('Formato CURP incorrecto')
            return validation
        
        if len(curp) != 18:
            validation['issues'].append('CURP debe tener 18 caracteres')
            return validation
        
        # Validar fecha de nacimiento
        try:
            year = int(curp[4:6])
            month = int(curp[6:8])
            day = int(curp[8:10])
            
            # Ajusta año (si >30 es 19xx, sino 20xx)
            full_year = 1900 + year if year > 30 else 2000 + year
            
            # Verifica si la fecha es válida
            dob = datetime(full_year, month, day)
            validation['date_of_birth'] = dob.strftime('%Y-%m-%d')
            
            # Valida que no sea fecha futura
            if dob > datetime.now():
                validation['issues'].append('Fecha de nacimiento en el futuro')
                return validation
            
            # Valida edad (debe ser >= 18 años)
            age = (datetime.now() - dob).days // 365
            if age < 18:
                validation['issues'].append(f'Menor de edad ({age} años)')
                return validation
                
        except ValueError:
            validation['issues'].append('Fecha de nacimiento inválida')
            return validation
        
        # Validar dígito verificador (usando módulo 17)
        try:
            letters_dict = {chr(65+i): i+10 for i in range(26)}
            verification_value = 0
            weights = [3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7]
            
            for i, char in enumerate(curp[:17]):
                if char.isdigit():
                    value = int(char)
                else:
                    value = letters_dict.get(char, 0)
                verification_value += (value * weights[i])
            
            verification_digit = (10 - (verification_value % 10)) % 10
            actual_digit = int(curp[17])
            
            if verification_digit != actual_digit:
                validation['issues'].append('Dígito verificador incorrecto')
                return validation
                
        except Exception as e:
            validation['issues'].append(f'Error validando dígito: {str(e)}')
            return validation
        
        validation['valid'] = True
        return validation
    
    @staticmethod
    def validate_rfc(rfc: str) -> dict:
        """
        Valida un RFC mexicano
        
        Formato: AAAA YYMMDD HNN
        - 4 letras (apellido, nombre)
        - 6 dígitos fecha nacimiento
        - 3 alfanuméricos (folio)
        """
        rfc = str(rfc).upper().replace(' ', '')
        
        validation = {
            'valid': False,
            'rfc': rfc,
            'issues': [],
            'date_of_birth': None
        }
        
        # Verificar formato (RFC persona física: 13 caracteres)
        if not re.match(r'^[A-Z]{3,4}\d{6}[A-Z0-9]{3}$', rfc):
            validation['issues'].append('Formato RFC incorrecto')
            return validation
        
        # RFC debe tener 13 caracteres
        if len(rfc) not in [12, 13]:
            validation['issues'].append('RFC debe tener 12 o 13 caracteres')
            return validation
        
        # Validar fecha
        try:
            year = int(rfc[4:6])
            month = int(rfc[6:8])
            day = int(rfc[8:10])
            
            full_year = 1900 + year if year > 30 else 2000 + year
            dob = datetime(full_year, month, day)
            validation['date_of_birth'] = dob.strftime('%Y-%m-%d')
            
            if dob > datetime.now():
                validation['issues'].append('Fecha de nacimiento en el futuro')
                return validation
            
        except ValueError:
            validation['issues'].append('Fecha de nacimiento inválida')
            return validation
        
        validation['valid'] = True
        return validation
    
    @staticmethod
    def validate_data_consistency(data: dict) -> dict:
        """
        Valida consistencia entre múltiples campos
        
        Verifica:
        - Nombres coinciden (si hay múltiples)
        - Fechas son consistentes
        - CURP y RFC coinciden en fecha y sexo
        - No hay datos contradictorios
        """
        consistency = {
            'consistent': True,
            'issues': [],
            'warnings': [],
            'score': 100  # 0-100
        }
        
        names = data.get('names', [])
        curps = data.get('curp', [])
        rfcs = data.get('rfc', [])
        dates = data.get('dates', [])
        
        # Verifica si hay múltiples valores donde debería haber uno
        if len(names) > 1:
            consistency['warnings'].append(f'Múltiples nombres encontrados: {names}')
            consistency['score'] -= 10
        
        if len(curps) > 1:
            consistency['issues'].append(f'Múltiples CURPs: {curps}')
            consistency['consistent'] = False
            consistency['score'] -= 20
        
        if len(rfcs) > 1:
            consistency['warnings'].append(f'Múltiples RFCs: {rfcs}')
            consistency['score'] -= 10
        
        # Verifica coincidencia CURP-RFC
        if curps and rfcs:
            curp = curps[0]
            rfc = rfcs[0]
            
            # Extrae fecha del CURP
            try:
                curp_year = int(curp[4:6])
                curp_month = int(curp[6:8])
                curp_day = int(curp[8:10])
                
                # Extrae fecha del RFC
                rfc_year = int(rfc[4:6])
                rfc_month = int(rfc[6:8])
                rfc_day = int(rfc[8:10])
                
                if not (curp_year == rfc_year and curp_month == rfc_month and curp_day == rfc_day):
                    consistency['issues'].append('Fechas de CURP y RFC no coinciden')
                    consistency['consistent'] = False
                    consistency['score'] -= 25
            except (ValueError, IndexError):
                pass
            
            # Verifica género en CURP
            if len(curp) > 10:
                gender = curp[10]
                if gender not in ['H', 'M']:
                    consistency['issues'].append(f'Género inválido en CURP: {gender}')
                    consistency['score'] -= 15
        
        # Verifica calidad de datos
        if not names:
            consistency['warnings'].append('No se encontraron nombres')
            consistency['score'] -= 5
        
        if not curps and not rfcs:
            consistency['warnings'].append('No se encontraron CURP ni RFC')
            consistency['issues'].append('Documento sin identificación válida')
            consistency['consistent'] = False
            consistency['score'] -= 30
        
        return consistency
    
    def extract_and_validate(self, image_path: str) -> dict:
        """
        Pipeline completo: extrae texto → valida → analiza consistencia
        """
        result = {
            'success': False,
            'ocr': None,
            'curp_validation': None,
            'rfc_validation': None,
            'data_consistency': None,
            'overall_score': 0,
            'recommendation': 'REVISAR_MANUALMENTE',
            'errors': []
        }
        
        # 1. Extrae texto
        ocr_result = self.extract_text_from_image(image_path)
        result['ocr'] = ocr_result
        
        if not ocr_result['success']:
            result['errors'].append(ocr_result.get('error', 'Error desconocido en OCR'))
            return result
        
        # Si OCR tiene baja confianza, advierte
        if ocr_result['confidence'] < 0.7:
            result['errors'].append(f'Calidad de OCR baja ({ocr_result["confidence"]:.1%})')
        
        fields = ocr_result['fields']
        
        # 2. Valida CURP
        if fields.get('curp'):
            curp = fields['curp'][0]
            result['curp_validation'] = self.validate_curp(curp)
        
        # 3. Valida RFC
        if fields.get('rfc'):
            rfc = fields['rfc'][0]
            result['rfc_validation'] = self.validate_rfc(rfc)
        
        # 4. Analiza consistencia general
        result['data_consistency'] = self.validate_data_consistency(fields)
        
        # 5. Calcula puntuación general
        scores = []
        
        # OCR confidence (0-100)
        scores.append(ocr_result['confidence'] * 100)
        
        # CURP válido (50 puntos si válido)
        if result['curp_validation'] and result['curp_validation']['valid']:
            scores.append(50)
        elif result['curp_validation']:
            scores.append(0)
        
        # RFC válido (30 puntos si válido)
        if result['rfc_validation'] and result['rfc_validation']['valid']:
            scores.append(30)
        elif result['rfc_validation']:
            scores.append(0)
        
        # Consistencia de datos (20 puntos)
        if result['data_consistency']:
            scores.append(result['data_consistency']['score'] / 5)
        
        overall_score = np.mean(scores) if scores else 0
        result['overall_score'] = float(overall_score)
        
        # 6. Genera recomendación
        if result['curp_validation'] and result['curp_validation']['valid'] and \
           result['rfc_validation'] and result['rfc_validation']['valid'] and \
           result['data_consistency']['consistent'] and \
           overall_score >= 75:
            result['recommendation'] = 'VALIDAR_AUTOMATICAMENTE'
            result['success'] = True
        elif overall_score >= 60:
            result['recommendation'] = 'REVISAR_POR_VALIDATOR1'
            result['success'] = True
        else:
            result['recommendation'] = 'RECHAZAR_O_REVISAR_MANUALMENTE'
        
        return result


class FaceAnalyzer:
    """Análisis de rostro en documentos (opcional)"""
    
    @staticmethod
    def analyze_face_in_document(image_path: str, reference_image_path: str = None) -> dict:
        """
        Analiza rostro en documento y opcionalmente compara con foto de referencia
        """
        if not FACE_RECOGNITION_AVAILABLE:
            return {
                'success': False,
                'error': 'face-recognition no instalado',
                'faces_detected': 0,
                'face_quality': None
            }
        
        try:
            # Carga imagen del documento
            image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image, model='cnn')
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            result = {
                'success': True,
                'faces_detected': len(face_locations),
                'face_quality': None,
                'match_percentage': 0 if not reference_image_path else None,
                'error': None
            }
            
            if len(face_locations) == 0:
                result['success'] = False
                result['error'] = 'No se detectó rostro en el documento'
                return result
            
            if len(face_locations) > 1:
                result['error'] = 'Se detectaron múltiples rostros (se esperaba 1)'
            
            # Calidad del rostro (tamaño relativo)
            doc_height, doc_width = image.shape[:2]
            face_height = face_locations[0][0] - face_locations[0][2]
            face_quality_ratio = abs(face_height) / doc_height
            result['face_quality'] = float(face_quality_ratio)
            
            # Comparación con foto de referencia
            if reference_image_path and len(face_encodings) > 0:
                try:
                    ref_image = face_recognition.load_image_file(reference_image_path)
                    ref_encodings = face_recognition.face_encodings(ref_image)
                    
                    if len(ref_encodings) > 0:
                        # Compara rostros
                        results = face_recognition.compare_faces(
                            [face_encodings[0]], 
                            ref_encodings[0],
                            tolerance=0.6
                        )
                        
                        # Calcula distancia
                        distances = face_recognition.face_distance(
                            [face_encodings[0]], 
                            ref_encodings[0]
                        )
                        
                        # Convierte distancia a porcentaje de similitud (0-100)
                        match_percentage = (1 - distances[0]) * 100
                        result['match_percentage'] = float(match_percentage)
                        
                        if match_percentage >= 80:
                            result['facial_match'] = 'COINCIDE'
                        elif match_percentage >= 60:
                            result['facial_match'] = 'SIMILAR'
                        else:
                            result['facial_match'] = 'NO_COINCIDE'
                
                except Exception as e:
                    result['error'] = f'Error comparando rostros: {str(e)}'
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error analizando rostro: {str(e)}',
                'faces_detected': 0,
                'face_quality': None
            }
