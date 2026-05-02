from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from .fields import EncryptedCharField, EncryptedTextField

User = get_user_model()

class Profile(models.Model):
    ROLE_CHOICES = [
        ("cliente", "Cliente"),
        ("validator1", "STAFF"),
        ("validator2", "SENIOR"),
        ("admin", "Administrador"),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_worker = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="cliente")

    def __str__(self):
        return f"Perfil de {self.user.username} ({self.get_role_display()})"

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

class Document(models.Model):
    STATUS_CHOICES = [
        ("pending_validator1", "Espera STAFF"),
        ("validator1_review", "En revisión STAFF"),
        ("pending_validator2", "Espera SENIOR"),
        ("validator2_review", "En revisión SENIOR"),
        ("approved", "Aprobado"),
        ("rejected", "Rechazado"),
    ]
    
    CREDIT_TYPE_CHOICES = [
        ("credito", "Crédito Personal"),
        ("tarjeta", "Tarjeta de Crédito"),
    ]
    
    REJECTION_REASONS = [
        ("ilegible", "Documento ilegible"),
        ("no_coinciden", "Datos no coinciden entre documentos"),
        ("curp_invalido", "CURP/RFC inválido o no existe"),
        ("buro_credito", "En buró de crédito"),
        ("otro", "Otro"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = EncryptedCharField(max_length=200)
    credit_type = models.CharField(max_length=20, choices=CREDIT_TYPE_CHOICES, default="credito")
    
    # Información personal
    nombre_completo = EncryptedCharField(max_length=255, null=True, blank=True)
    domicilio = EncryptedCharField(max_length=500, null=True, blank=True)
    telefono = EncryptedCharField(max_length=20, null=True, blank=True)
    curp = EncryptedCharField(max_length=18, null=True, blank=True)
    curp_documento = models.FileField(upload_to="uploads/%Y/%m/%d/docs/", null=True, blank=True)
    rfc = EncryptedCharField(max_length=13, null=True, blank=True)
    
    # Datos extraídos por OCR (para comparación)
    ocr_nombre = models.CharField(max_length=255, null=True, blank=True)
    ocr_curp = models.CharField(max_length=18, null=True, blank=True)
    ocr_rfc = models.CharField(max_length=13, null=True, blank=True)
    
    # Documentos
    acta_nacimiento = models.FileField(upload_to="uploads/%Y/%m/%d/docs/", null=True, blank=True)
    comprobante_domicilio = models.FileField(upload_to="uploads/%Y/%m/%d/docs/", null=True, blank=True)
    ine = models.FileField(upload_to="uploads/%Y/%m/%d/docs/", null=True, blank=True)
    comprobante_bancario = models.FileField(upload_to="uploads/%Y/%m/%d/docs/", null=True, blank=True)
    constancia_fiscal = models.FileField(upload_to="uploads/%Y/%m/%d/docs/", null=True, blank=True)
    
    # Campos adicionales
    file = models.FileField(upload_to="uploads/%Y/%m/%d/", null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="pending_validator1")
    
    # Usuarios
    validator1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="validator1_documents",
    )
    validator1_approved = models.BooleanField(null=True, blank=True)
    validator1_comment = EncryptedTextField(blank=True, null=True)
    validator1_date = models.DateTimeField(null=True, blank=True)
    
    validator2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="validator2_documents",
    )
    validator2_approved = models.BooleanField(null=True, blank=True)
    validator2_comment = EncryptedTextField(blank=True, null=True)
    validator2_date = models.DateTimeField(null=True, blank=True)
    
    rejection_reason = models.CharField(max_length=20, choices=REJECTION_REASONS, null=True, blank=True)
    rejection_details = EncryptedTextField(blank=True, null=True)
    
    erp_exported = models.BooleanField(default=False)
    erp_export_date = models.DateTimeField(null=True, blank=True)
    
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_documents",
    )
    clicked_continuidad = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.user.username})"

    def assign_worker(self):
        if self.assigned_to:
            return
        from django.contrib.auth import get_user_model
        from django.db.models import Count, Q
        User = get_user_model()
        
        # Buscar todos los STAFF
        staff_users = list(User.objects.filter(
            profile__role="validator1",
            profile__is_worker=True
        ))
        
        if not staff_users:
            return
        
        # Contar documentos pendientes de cada STAFF
        pending_counts = (
            Document.objects
            .filter(user__in=staff_users)
            .values('assigned_to')
            .filter(Q(status='pending') | Q(status='pending_validator1'))
            .annotate(count=Count('id'))
            .values_list('assigned_to', 'count')
        )
        
        count_map = dict(pending_counts)
        
        # Asignar al que tenga menos pendientes
        least_loaded = min(staff_users, key=lambda u: count_map.get(u.id, 0))
        self.assigned_to = least_loaded
        self.save()

class DocumentComment(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    comment = EncryptedTextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comentario de {self.author} sobre {self.document}"

class DocumentHistory(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="history")
    status = models.CharField(max_length=20)
    note = EncryptedTextField(blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.document.title}: {self.status} ({self.created_at:%Y-%m-%d %H:%M})"

class AuditLog(models.Model):
    table_name = models.CharField(max_length=100)
    row_pk = models.IntegerField()
    action = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    old_status = models.CharField(max_length=50, blank=True, null=True)
    new_status = models.CharField(max_length=50, blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Registro de auditoría"
        verbose_name_plural = "Registros de auditoría"

    def __str__(self):
        return f"{self.table_name} {self.action} ({self.changed_at:%Y-%m-%d %H:%M})"


class ERPExport(models.Model):
    """Modelo que simula la BD del ERP"""
    document = models.OneToOneField(Document, on_delete=models.CASCADE, related_name="erp_record")
    nombre_completo = EncryptedCharField(max_length=255)
    curp = EncryptedCharField(max_length=18)
    rfc = EncryptedCharField(max_length=13)
    domicilio = EncryptedCharField(max_length=500)
    telefono = EncryptedCharField(max_length=20)
    credit_type = models.CharField(max_length=20)
    exported_at = models.DateTimeField(auto_now_add=True)
    exported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Exportación a ERP"
        verbose_name_plural = "Exportaciones a ERP"

    def __str__(self):
        return f"ERP: {self.nombre_completo} ({self.exported_at:%Y-%m-%d})"
