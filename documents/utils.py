import os
import re
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
    import fitz
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

_ocr_instance = None


def _get_ocr():
    global _ocr_instance
    if _ocr_instance is None and PADDLEOCR_AVAILABLE:
        try:
            _ocr_instance = PaddleOCR(use_angle_cls=True, lang='es')
        except Exception as e:
            print(f"Error inicializando OCR: {e}")
            _ocr_instance = None
    return _ocr_instance


def _pdf_to_images(pdf_path: str, dpi: int = 200) -> list:
    """
    Conviert un PDF a lista de imagenes PNG en memoria.
    Usa PyMuPDF (fitz) que no requiere dependencias externas.
    """
    if not PYPDF_AVAILABLE:
        return []

    try:
        doc = fitz.open(pdf_path)
        images = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            mat = fitz.Matrix(dpi / 72, dpi / 72)
            pix = page.get_pixmap(matrix=mat)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(img)
        doc.close()
        return images
    except Exception as e:
        print(f"Error convirtiendo PDF: {e}")
        return []


def _ocr_image(image) -> list:
    """
    Ejecuta OCR en una imagen (PIL.Image o path string).
    Retorna lista de (texto, confianza).
    """
    ocr = _get_ocr()
    if not ocr:
        return []

    try:
        if isinstance(image, str):
            if not os.path.exists(image):
                return []
            result = ocr.ocr(image, cls=True)
        else:
            import cv2
            import tempfile
            import numpy as np
            img_array = np.array(image.convert("RGB"))
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                cv2.imwrite(tmp.name, img_bgr)
                tmp_path = tmp.name
            try:
                result = ocr.ocr(tmp_path, cls=True)
            finally:
                os.unlink(tmp_path)

        if not result or not result[0]:
            return []

        texts = []
        for line in result[0]:
            for word_info in line:
                text = word_info[1][0]
                confidence = word_info[1][1]
                texts.append((text, confidence))
        return texts
    except Exception as e:
        print(f"Error en OCR: {e}")
        return []


def _extract_fields_from_texts(texts: list) -> dict:
    """
    Extrae campos importantes de una lista de (texto, confianza).
    """
    full_text = " ".join(t[0] for t in texts)
    lines = full_text.replace("|", "\n").split("\n")
    avg_confidence = np.mean([t[1] for t in texts]) if texts else 0

    fields = {
        "curp": [],
        "rfc": [],
        "nombres": [],
        "domicilio": [],
        "telefono": [],
        "email": [],
        "fechas": [],
        "ocupacion": [],
        "estado_civil": [],
        "cp": [],
    }

    text_upper = full_text.upper()
    text_clean = re.sub(r"[\s\-\.]+", " ", text_upper)

    curp_pattern = r'([A-Z]{4})[\s\-\.]*(\d{6})[\s\-\.]*([HM])[\s\-\.]*([A-Z]{3})[\s\-\.]*([A-Z0-9]{2})[\s\-\.]*(\d)'
    for match in re.finditer(curp_pattern, text_clean):
        curp = "".join(match.groups())
        if len(curp) == 18:
            fields["curp"].append(curp)

    rfc_pattern = r'\b([A-Z]{3,4}\d{6}[A-Z0-9]{3,6})\b'
    for match in re.finditer(rfc_pattern, text_upper):
        rfc = match.group(1)
        if not any(rfc in c for c in fields["curp"]):
            fields["rfc"].append(rfc)

    name_labels = [
        r'(?:nombre(?:\s+completo)?|solicitante|nombre\s+del\s+titular|nombre)[:\s]+([A-Z\u00C0-\u00DC][A-Za-z\u00C0-\u00DC\u00E0-\u00FC]+(?:\s+[A-Z\u00C0-\u00DC\u00E0-\u00FC]+){1,4})',
        r'(?:nombres?|NOMBRE)\s*[:\.]?\s*([A-Z][A-Z\u00C0-\u00DC\u00E0-\u00FC\s]{3,60})',
    ]
    for pattern in name_labels:
        for match in re.finditer(pattern, full_text, re.IGNORECASE):
            name = match.group(1).strip()
            name = re.sub(r"\s+", " ", name)
            if 5 < len(name) < 80:
                fields["nombres"].append(name)

    if not fields["nombres"]:
        stop_words = {
            "DE", "DEL", "LA", "LOS", "LAS", "EL", "Y", "EN", "COMPROBANTE",
            "DOMICILIO", "NOMBRE", "RFC", "CURP", "FECHA", "NACIMIENTO",
            "ESTADO", "MUNICIPIO", "CIUDAD", "OCUPACION", "CIVIL", "TEL",
            "TELEFONO", "EMAIL", "CORREO", "CALLE", "NUMERO", "COLONIA",
            "CODIGO", "POSTAL", "SOLICITUD", "CREDITO", "TARJETA", "DOCUMENTO",
            "CONSTANCIA", "FISCAL", "SITUACION", "ACTA", "INE", "BANCARIO",
            "VIGENCIA", "CLABE", "CUENTA", "INSTITUCION", "ACTUAL", "RECIENTE",
            "SOLTERO", "CASADO", "DIVORCIADO", "VIUDO", "INGENIERO", "LICENCIADO",
            "ABOGADO", "DOCTOR", "CONTADOR", "EMPLEADO", "EMPRESARIO",
        }
        for line in lines:
            line = line.strip()
            if len(line) < 10 or len(line) > 80:
                continue
            if line.isupper() and ":" not in line:
                continue
            if re.match(r"^[A-Z\s:.,#/]+-?\d*$", line):
                continue
            parts = line.split()
            good_parts = [p for p in parts if p.upper() not in stop_words and len(p) > 2]
            if len(good_parts) >= 2:
                candidate = " ".join(good_parts[:4])
                if 5 < len(candidate) < 80 and not re.match(r"^\d", candidate):
                    fields["nombres"].append(candidate.title())

    fields["nombres"] = list(set(fields["nombres"]))
    fields["nombres"].sort(key=len, reverse=True)

    addr_patterns = [
        r'(?:CALLE|AV|AVENIDA|CARRERA|BLVD|BOULEVARD|CDA|PASAJE|CALLEJON)[\s\.:,]([^\n]{10,100})',
        r'(?:DOMICILIO|DIRECCION|RESIDENCIA)[:\s]+([^\n]{10,150})',
        r'(?:COLONIA|COL|BARRIO|FRACC|FRACCIONMENTO)[:\s]+([^\n]{5,80})',
        r'(?:DELEGACION|ALCALDIA|MUNICIPIO)[:\s]+([^\n]{5,60})',
    ]
    for pattern in addr_patterns:
        for match in re.finditer(pattern, full_text, re.IGNORECASE):
            addr = match.group(1).strip()
            if addr and len(addr) > 5:
                fields["domicilio"].append(addr)

    fields["domicilio"] = list(set(fields["domicilio"]))

    phone_pattern = r'(?:TEL(?:EFONO)?|CELULAR|MOVIL|TELEFONO)[:\s]*([\d\s\-\(\)]{7,15})'
    for match in re.finditer(phone_pattern, full_text, re.IGNORECASE):
        phone = re.sub(r"[^\d]", "", match.group(1))
        if len(phone) >= 10:
            fields["telefono"].append(phone)

    bare_phones = re.findall(r'\b(\d{10})\b', full_text)
    for phone in bare_phones:
        if phone not in fields["telefono"]:
            fields["telefono"].append(phone)
    fields["telefono"] = list(set(fields["telefono"]))

    email_pattern = r'\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})\b'
    emails = re.findall(email_pattern, full_text)
    fields["email"] = list(set(emails))

    date_patterns = [
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
        r'(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})',
    ]
    for pattern in date_patterns:
        dates = re.findall(pattern, full_text, re.IGNORECASE)
        fields["fechas"].extend(dates)
    fields["fechas"] = list(set(fields["fechas"]))

    occ_keywords = r'(?:INGENIERO|ABOGADO|DOCTOR|M[EÉ]DICO|CONTADOR|EMPRESARIO|EMPLEADO|TRABAJADOR|DOCENTE|PROFESOR|T[\EÉ]CNICO|ADMINISTRADOR|GERENTE|DIRECTOR|JEFE|SUPERVISOR|VENDEDOR|COMERCIANTE|TRANSPORTISTA|AGRICULTOR|MEC[\AÁ]NICO|ELECTRICISTA|PLOMERO|CONSTRUCTOR|PSIC[\OÓ]LOGO|ENFERMER[AO]|ARQUITECTO|CONTADOR P[UU]BLICO|LICENCIADO|DISE[ÑN]ADOR|PROGRAMADOR|ANALISTA|CONTADUR[IÍ]A|INGENIER[IÍ]A)'
    occupations = re.findall(occ_keywords, full_text, re.IGNORECASE)
    fields["ocupacion"] = list(set(occupations))

    marital_keywords = r'(?:SOLTER[AO]|CASAD[AO]|DIVORCIAD[AO]|VIUD[AO]|UNI[OÓ]N LIBRE)'
    marital = re.findall(marital_keywords, full_text, re.IGNORECASE)
    fields["estado_civil"] = list(set(marital))

    cp_pattern = r'(?:C[\OÓ]DIGO POSTAL|C\.?P\.?)[\s:]*(\d{5})'
    for match in re.finditer(cp_pattern, full_text, re.IGNORECASE):
        fields["cp"].append(match.group(1))

    return {
        "nombre": fields["nombres"][0] if fields["nombres"] else None,
        "curp": fields["curp"][0] if fields["curp"] else None,
        "rfc": fields["rfc"][0] if fields["rfc"] else None,
        "domicilio": " ".join(fields["domicilio"][:2]) if fields["domicilio"] else None,
        "telefono": fields["telefono"][0] if fields["telefono"] else None,
        "email": fields["email"][0] if fields["email"] else None,
        "ocupacion": fields["ocupacion"][0] if fields["ocupacion"] else None,
        "estado_civil": fields["estado_civil"][0] if fields["estado_civil"] else None,
        "raw_fields": fields,
        "confidence": float(avg_confidence),
    }


def extract_text_from_pdf(file_path: str) -> dict:
    """
    Extrae datos reales de un archivo (PDF o imagen) usando OCR.
    Soporta: .pdf, .png, .jpg, .jpeg, .gif, .webp
    """
    file_path = str(file_path)

    if not os.path.exists(file_path):
        return {"nombre": None, "curp": None, "rfc": None, "error": "Archivo no encontrado"}

    ext = Path(file_path).suffix.lower()

    images = []
    if ext == ".pdf":
        images = _pdf_to_images(file_path)
    elif ext in (".png", ".jpg", ".jpeg", ".gif", ".webp"):
        try:
            images.append(Image.open(file_path).convert("RGB"))
        except Exception as e:
            return {"nombre": None, "curp": None, "rfc": None, "error": str(e)}
    else:
        return {"nombre": None, "curp": None, "rfc": None, "error": f"Formato no soportado: {ext}"}

    if not images:
        return {"nombre": None, "curp": None, "rfc": None, "error": "No se pudieron procesar las im\u00e1genes"}

    best_result = None
    best_score = 0

    for img in images:
        texts = _ocr_image(img)
        if not texts:
            continue

        fields = _extract_fields_from_texts(texts)

        score = 0
        if fields.get("curp"):
            score += 50
        if fields.get("rfc"):
            score += 30
        if fields.get("nombre"):
            score += 20
        score += fields.get("confidence", 0) * 10

        if score > best_score:
            best_score = score
            best_result = fields

    if best_result:
        return best_result

    return {"nombre": None, "curp": None, "rfc": None, "error": "No se detectaron datos v\u00e1lidos"}


from django.core.mail import send_mail
from django.conf import settings


def send_rejection_email(user_email, user_name, reason, details):
    """Envia correo de rechazo al cliente"""
    reason_text = {
        "ilegible": "Documento ilegible",
        "no_coinciden": "Datos no coinciden entre documentos",
        "curp_invalido": "CURP/RFC invalido o no existe",
        "buro_credito": "En buro de credito",
        "otro": "Otro",
    }
    subject = "Solicitud de credito/tarjeta rechazada"
    message = f"""Hola {user_name},

Lamentablemente, tu solicitud de credito/tarjeta ha sido rechazada por la siguiente razon:

Motivo: {reason_text.get(reason, reason)}
Detalles: {details}

Puedes editar tu informacion y reenviar tu solicitud en tu perfil.

Saludos,
Equipo de Validacion Bancaria"""
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email], fail_silently=False)
        return True
    except Exception as e:
        print(f"Error enviando correo: {e}")
        return False


def send_approval_email(user_email, user_name, credit_type, approval_reason=""):
    """Envia correo de aprobacion al cliente"""
    subject = "Tu solicitud ha sido aprobada!"
    reason_section = f"\nMotivo de Aprobacion:\n{approval_reason}\n" if approval_reason else ""
    message = f"""Hola {user_name},

Excelentes noticias! Tu solicitud de {credit_type} ha sido aprobada.{reason_section}
Por favor de revisar su perfil nuevamente en la pagina para seguir con su proceso.

Gracias por tu confianza,
Equipo de Validacion Bancaria"""
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email], fail_silently=False)
        return True
    except Exception as e:
        print(f"Error enviando correo: {e}")
        return False


def send_validator_notification(validator_email, document_id, status):
    """Notifica al validador sobre un nuevo documento"""
    subject = f"Nuevo documento para validacion (#{document_id})"
    message = f"""Hay un nuevo documento esperando tu revision.

ID del Documento: {document_id}
Estado: {status}

Accede al panel de validacion para revisar."""
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [validator_email], fail_silently=False)
        return True
    except Exception as e:
        print(f"Error enviando correo: {e}")
        return False
