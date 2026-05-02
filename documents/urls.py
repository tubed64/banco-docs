from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("change-password/", views.change_password_required, name="change_password_required"),
    path("worker/", views.worker_panel, name="worker_panel"),
    path("document/<int:pk>/", views.document_detail, name="document_detail"),
    path("validator1/", views.validator1_panel, name="validator1_panel"),
    path("validator1/<int:pk>/", views.validator1_review, name="validator1_review"),
    path("validator2/", views.validator2_panel, name="validator2_panel"),
    path("validator2/<int:pk>/", views.validator2_review, name="validator2_review"),
    
    # Admin Dashboard
    path("dashboard-admin/", views.admin_panel, name="admin_panel"),
    path("dashboard-admin/audit-log/", views.admin_audit_log, name="admin_audit_log"),
    path("dashboard-admin/validator/<int:pk>/edit/", views.admin_edit_validator, name="admin_edit_validator"),
    path("dashboard-admin/validator/<int:pk>/delete/", views.admin_delete_validator, name="admin_delete_validator"),
    path("dashboard-admin/download-approved/", views.download_approved_documents, name="download_approved_documents"),
    path("dashboard-admin/monthly-extraction/", views.monthly_extraction, name="monthly_extraction"),
    path("dashboard-admin/monthly-extraction/export/", views.export_monthly_excel, name="export_monthly_excel"),
    path("dashboard-admin/monthly-extraction/delete/", views.delete_monthly_documents, name="delete_monthly_documents"),
    path("document/<int:pk>/continuidad/", views.click_continuidad, name="click_continuidad"),
]
