import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-replace-this-key-with-a-real")
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() in ("1", "true", "yes")

# Accept requests from any hostname so Railway's load balancer always reaches Django.
# The DJANGO_ALLOWED_HOSTS env var can restrict this to specific domains in production.
_allowed_hosts_env = os.getenv("DJANGO_ALLOWED_HOSTS", "")
if _allowed_hosts_env:
    ALLOWED_HOSTS = _allowed_hosts_env.split(",")
else:
    ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = os.getenv(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    "https://banco-web.railway.app",
).split(",")

# Railway terminates TLS at the load balancer and forwards plain HTTP to Gunicorn,
# so we must NOT redirect HTTP→HTTPS inside Django (that would cause redirect loops).
# SECURE_SSL_REDIRECT is disabled by default; set DJANGO_SECURE_SSL_REDIRECT=true only
# if you are running Django behind a proxy that does NOT strip the HTTPS scheme.
SECURE_SSL_REDIRECT = os.getenv("DJANGO_SECURE_SSL_REDIRECT", "false").lower() in ("1", "true", "yes")
# Trust Railway's load-balancer forwarded-proto header so Django knows the original
# request was HTTPS even though Gunicorn received plain HTTP.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "documents",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "documents.middleware.ForcePasswordChangeMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "banking.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "banking.wsgi.application"

# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Use PostgreSQL if DATABASE_URL is available (Neon)
try:
    import dj_database_url
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        DATABASES["default"] = dj_database_url.parse(db_url, conn_max_age=600)
        DATABASES["default"]["ENGINE"] = "django.db.backends.postgresql"
        # SSL settings for Neon
        DATABASES["default"]["OPTIONS"] = {
            "sslmode": "require",
        }
except ImportError:
    pass

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "es-mx"
TIME_ZONE = "America/Mexico_City"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "documents" / "static"]
# WhiteNoise: serve compressed, cache-busted static files in production
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
# Railway and Render both need a writable path for uploaded files
_media_root_env = os.getenv("MEDIA_ROOT")
if _media_root_env:
    MEDIA_ROOT = _media_root_env
elif os.getenv("RENDER"):
    MEDIA_ROOT = "/tmp/media"
else:
    MEDIA_ROOT = BASE_DIR / "media"
os.makedirs(str(MEDIA_ROOT), exist_ok=True)

LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"
LOGIN_URL = "login"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Encryption Configuration
FERNET_KEY = os.getenv("FERNET_KEY", "c2V_lsFZtVxZ6H7bOzHvTlXoHv3cZQZxZ6H7bOzHvTlXo=")

# Email Configuration
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() in ("1", "true", "yes")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@bancovalidacion.com")
