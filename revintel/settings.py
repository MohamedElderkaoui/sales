"""
Django settings for revintel project.
Adaptado para un dashboard analítico (dev + recomendaciones de producción).
Compatible con Django 5.2.x
"""

import os
from pathlib import Path

# ----------------------------------------
# Base
# ----------------------------------------
# Apunta a la raíz del proyecto (donde suele estar manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------------------------------
# Entorno / Seguridad
# ----------------------------------------
# Recomendado: exportar DJANGO_SECRET_KEY en el entorno o usar un secret manager
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-secret-key-revintel")

def env_bool(name: str, default: bool = False) -> bool:
    val = os.environ.get(name)
    if val is None:
        return default
    return val.lower() in ("1", "true", "yes", "on")

DEBUG = env_bool("DJANGO_DEBUG", True)

# ALLOWED_HOSTS parseado desde CSV
ALLOWED_HOSTS = [h.strip() for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h.strip()]

# CSRF trusted origins (CSV), limpio de valores vacíos
CSRF_TRUSTED_ORIGINS = [u.strip() for u in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if u.strip()]

# ----------------------------------------
# Aplicaciones instaladas
# ----------------------------------------
INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Postgres helpers
    "django.contrib.postgres",

    # 3rd party
    "rest_framework",
    "django_filters",

    # Local apps
    "sales",
    "analytics",
    "dashboard",
    "reports",
    "users",
]

# ----------------------------------------
# Middleware
# ----------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise (si lo usas) inmediatamente después de SecurityMiddleware
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "revintel.urls"

# ----------------------------------------
# Templates
# ----------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "revintel.wsgi.application"
ASGI_APPLICATION = os.environ.get("DJANGO_ASGI_APPLICATION", "revintel.asgi.application")

# ----------------------------------------
# Base de datos
# ----------------------------------------
# Uso sencillo de Postgres con variables de entorno; si quieres usar DATABASE_URL,
# instala dj-database-url y úsalo aquí.
if os.environ.get("POSTGRES_DB"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB"),
            "USER": os.environ.get("POSTGRES_USER"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
            "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ----------------------------------------
# Password validation
# ----------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ----------------------------------------
# Internacionalización / Zona horaria
# ----------------------------------------
LANGUAGE_CODE = os.environ.get("DJANGO_LANGUAGE_CODE", "es-es")
TIME_ZONE = os.environ.get("DJANGO_TIME_ZONE", "Europe/Madrid")
USE_I18N = True
USE_TZ = True

# ----------------------------------------
# Archivos estáticos y media
# ----------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [BASE_DIR / "static"]

# WhiteNoise sólo necesario/útil en producción - usa condicional si quieres:
if not DEBUG:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ----------------------------------------
# REST framework
# ----------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": int(os.environ.get("DJANGO_PAGE_SIZE", 25)),
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
}

# ----------------------------------------
# Autenticación
# ----------------------------------------
AUTH_USER_MODEL = os.environ.get("DJANGO_AUTH_USER_MODEL", "users.RevUser")

# ----------------------------------------
# WeasyPrint
# ----------------------------------------
WEASYPRINT_BASEURL = STATIC_ROOT

# ----------------------------------------
# Logging
# ----------------------------------------
LOG_LEVEL = os.environ.get("DJANGO_LOG_LEVEL", "INFO").upper()
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "%(levelname)s %(asctime)s %(name)s %(message)s"},
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
    },
    "root": {"handlers": ["console"], "level": LOG_LEVEL},
}

# ----------------------------------------
# Seguridad adicional para producción (activar si DEBUG=False)
# ----------------------------------------
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", True)
    SECURE_HSTS_SECONDS = int(os.environ.get("DJANGO_SECURE_HSTS_SECONDS", 3600))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", True)
    SECURE_HSTS_PRELOAD = env_bool("DJANGO_SECURE_HSTS_PRELOAD", False)
    X_FRAME_OPTIONS = "DENY"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
