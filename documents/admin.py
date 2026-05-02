from django.contrib import admin
from .models import Document, DocumentComment, Profile, DocumentHistory, AuditLog

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "is_worker")
    list_filter = ("is_worker",)
    search_fields = ("user__username", "user__email")

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("table_name", "action", "row_pk", "changed_by", "changed_at")
    list_filter = ("table_name", "action")
    search_fields = ("note", "table_name")

@admin.register(DocumentHistory)
class DocumentHistoryAdmin(admin.ModelAdmin):
    list_display = ("document", "status", "author", "created_at")
    list_filter = ("status",)
    search_fields = ("document__title", "author__username")

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "uploaded_at", "assigned_to")
    list_filter = ("status",)
    search_fields = ("user__username", "assigned_to__username")

@admin.register(DocumentComment)
class DocumentCommentAdmin(admin.ModelAdmin):
    list_display = ("document", "author", "created_at")
    search_fields = ("document__id", "author__username")
