import base64
import os

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.db import models


def get_fernet():
    key = getattr(settings, "FERNET_KEY", None)
    if not key:
        raise ValueError("FERNET_KEY no está configurada en settings.py o .env")
    if isinstance(key, str):
        key = key.encode()
    return Fernet(key)


class EncryptedTextField(models.TextField):
    description = "Text field that is encrypted in the database."

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        try:
            return get_fernet().decrypt(value.encode()).decode()
        except (InvalidToken, AttributeError):
            return value

    def get_prep_value(self, value):
        if value is None:
            return value
        if isinstance(value, str):
            return get_fernet().encrypt(value.encode()).decode()
        return value

    def to_python(self, value):
        if value is None:
            return value
        if isinstance(value, str):
            try:
                return get_fernet().decrypt(value.encode()).decode()
            except (InvalidToken, AttributeError):
                return value
        return value


class EncryptedCharField(models.CharField):
    description = "Char field that is encrypted in the database."

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        try:
            return get_fernet().decrypt(value.encode()).decode()
        except (InvalidToken, AttributeError):
            return value

    def get_prep_value(self, value):
        if value is None:
            return value
        if isinstance(value, str):
            return get_fernet().encrypt(value.encode()).decode()
        return value

    def to_python(self, value):
        if value is None:
            return value
        if isinstance(value, str):
            try:
                return get_fernet().decrypt(value.encode()).decode()
            except (InvalidToken, AttributeError):
                return value
        return value
