"""
Django settings for revintel project.

Adaptado para un dashboard analítico (dev + recomendaciones de producción).
Django 5.2.11 compatible.
"""

import os
from pathlib import Path

# ----------------------------------------
# Base
# ----------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
print(f"BASE_DIR: {BASE_DIR}")  # útil para debug, eliminar en producción

# Carga opcional de .env si quieres (si instalas python-dotenv)
# from dotenv import load_dotenv
# load_dotenv(BASE_DIR / ".env")

# ----------------------------------------
# Seguridad / Entorno
# ----------------------------------------
# En desarrollo puedes dejar DEBUG=True, en producción pon DEBUG=False y
# exporta las variables de entorno correspondientes.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-secret-key-revintel")  # cambia en prod
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"

# Configura ALLOWED_HOSTS por entorno (ej: 'revintel.example.com,localhost')
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Orígenes de confianza para CSRF (útil en producción con HTTPS)
CSRF_TRUSTED_ORIGINS = [x for x in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if x]
# Ejemplo: export DJANGO_CSRF_TRUSTED_ORIGINS="https://revintel.example.com"

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

    # Postgres specific helpers (SearchVector, GinIndex, ArrayField, JSONField compat)
    "django.contrib.postgres",

    # 3rd party
    "rest_framework",
    "django_filters",

    # Optional: añadir si usas whitenoise estático en producción
    # No es estrictamente necesario en INSTALLED_APPS, pero pip instala whitenoise.
    # "whitenoise.runserver_nostatic",

    # Apps locales
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
    # WhiteNoise (serve static files in production without nginx, si lo instalas)
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.middleware.security.SecurityMiddleware",
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
        # Añadimos una carpeta global de templates en BASE_DIR / "templates"
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
print(f"TEMPLATES DIRS: {TEMPLATES[0]['DIRS']}")  # debug, eliminar en producción
WSGI_APPLICATION = "revintel.wsgi.application"
ASGI_APPLICATION = "revintel.asgi.application"  # si usas Channels después

# ----------------------------------------
# Base de datos
# ----------------------------------------
# Por defecto utiliza SQLite para desarrollo local.
# Para producción, define las variables POSTGRES_* ó configura DATABASE_URL y usa dj-database-url.
if os.environ.get("POSTGRES_DB"):
    # Configuración sencilla para Postgres usando variables de entorno
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
    # Fallback SQLite (conveniente para desarrollo rápido)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
print(f"DATABASES: {DATABASES}")  # debug, eliminar en producción
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
# Para tu desarrollo y despliegue en España:
LANGUAGE_CODE = "en-us"
TIME_ZONE = os.environ.get("DJANGO_TIME_ZONE", "Europe/Madrid")
USE_I18N = True
USE_TZ = True
if DEBUG:
    print(f"[DEBUG] LANGUAGE_CODE={LANGUAGE_CODE}, TIME_ZONE={TIME_ZONE}, USE_I18N={USE_I18N}, USE_TZ={USE_TZ}")
# ----------------------------------------
# Archivos estáticos y media
# ----------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR.parent / "staticfiles"  # collectstatic guardará aquí (producción)
STATICFILES_DIRS = [
    BASE_DIR/ "static",  # lugar para tus assets durante desarrollo
]

# WhiteNoise configuration (genera archivos estáticos comprimidos en producción)
# Recomendado instalar whitenoise y ejecutar collectstatic antes de desplegar.
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR.parent / "media"

# ----------------------------------------
# REST framework y filtros
# ----------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 25,
    # Añade autenticación según tu elección: SessionAuthentication, Token, JWT...
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
}

# ----------------------------------------
# Autenticación (si extiendes user)
# ----------------------------------------
# Si usas users.RevUser, necesitas descomentar la siguiente línea.
# IMPORTANTE: Si ya tienes migraciones con el User por defecto, deberás recrear la BD.
AUTH_USER_MODEL = "users.RevUser"

# ----------------------------------------
# WeasyPrint / generación PDF
# ----------------------------------------
# Nota: WeasyPrint requiere librerías del sistema (cairo, pango, gdk-pixbuf) — revisa docs.
WEASYPRINT_BASEURL = STATIC_ROOT  # útil para resolver rutas a CSS al generar PDFs

# ----------------------------------------
# Logging básico
# ----------------------------------------
LOG_LEVEL = os.environ.get("DJANGO_LOG_LEVEL", "INFO")

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
# Seguridad adicional para producción
# ----------------------------------------
# En producción, activa estas opciones (comentadas aquí para que no rompan dev):
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_BROWSER_XSS_FILTER = True
# SECURE_CONTENT_TYPE_NOSNIFF = True
# SECURE_SSL_REDIRECT = True  # fuerza HTTPS
# SECURE_HSTS_SECONDS = 3600  # HSTS
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# ----------------------------------------
# Default primary key and otros
# ----------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ----------------------------------------
# Información extra / Tips
# ----------------------------------------
# - Para usar Postgres en local, exporta:
#   export POSTGRES_DB=revintel_db
#   export POSTGRES_USER=revintel_user
#   export POSTGRES_PASSWORD=secret
#   export POSTGRES_HOST=localhost
#
# - Para producción, NO dejes SECRET_KEY en el repositorio. Usa variables de entorno o un secret manager.
#
# - Para servir estáticos en producción sin nginx, instala whitenoise:
#   pip install whitenoise
#   y asegúrate de ejecutar `python manage.py collectstatic` antes de desplegar.
#
# - Para PDFs con WeasyPrint en Linux, instala dependencias del sistema (ej.: apt install libcairo2 libpango-1.0-0 libgdk-pixbuf2.0-0).
#
# - Si quieres cargar variables desde un .env durante el desarrollo, instala python-dotenv y
#   descomenta las líneas de carga al comienzo del archivo.
#
# - Si vas a desplegar en servicios como Render o Railway, configura las variables de entorno en la plataforma.
