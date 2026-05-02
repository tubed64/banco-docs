from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Document, DocumentComment

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Correo electrónico"}))

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control", "placeholder": "Usuario"})
        self.fields["password1"].widget.attrs.update({"class": "form-control", "placeholder": "Contraseña"})
        self.fields["password2"].widget.attrs.update({"class": "form-control", "placeholder": "Repetir contraseña"})

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = [
            "credit_type",
            "nombre_completo",
            "domicilio",
            "telefono",
            "curp",
            "curp_documento",
            "rfc",
            "acta_nacimiento",
            "comprobante_domicilio",
            "ine",
            "comprobante_bancario",
            "constancia_fiscal",
        ]
        widgets = {
            "credit_type": forms.Select(attrs={"class": "form-control"}),
            "nombre_completo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre completo"}),
            "domicilio": forms.TextInput(attrs={"class": "form-control", "placeholder": "Domicilio"}),
            "telefono": forms.TextInput(attrs={"class": "form-control", "placeholder": "Teléfono"}),
            "curp": forms.TextInput(attrs={"class": "form-control", "placeholder": "CURP"}),
            "curp_documento": forms.FileInput(attrs={"class": "form-control"}),
            "rfc": forms.TextInput(attrs={"class": "form-control", "placeholder": "RFC"}),
            "acta_nacimiento": forms.FileInput(attrs={"class": "form-control"}),
            "comprobante_domicilio": forms.FileInput(attrs={"class": "form-control"}),
            "ine": forms.FileInput(attrs={"class": "form-control"}),
            "comprobante_bancario": forms.FileInput(attrs={"class": "form-control"}),
            "constancia_fiscal": forms.FileInput(attrs={"class": "form-control"}),
        }

class DocumentCorrectionForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["file", "curp_documento"]
        widgets = {
            "file": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "curp_documento": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

class DocumentCommentForm(forms.ModelForm):
    class Meta:
        model = DocumentComment
        fields = ["comment"]
        widgets = {
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Explica por qué se rechaza o qué necesita corregir..."}),
        }
