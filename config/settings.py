"""
Django settings for SaaS Payment project.
Production-grade configuration with PostgreSQL, JWT, and Stripe.
"""
import os
import sys
from datetime import timedelta
from pathlib import Path

import dj_database_url

from decouple import Csv, config

# ─── Base Directory ───────────────────────────────────────────────
BASE_DIR: Path = Path(__file__).resolve().parent.parent

# ─── Security ─────────────────────────────────────────────────────
SECRET_KEY: str = config('DJANGO_SECRET_KEY')
DEBUG: bool = config('DJANGO_DEBUG', default=False, cast=bool)
ALLOWED_HOSTS: list[str] = config('DJANGO_ALLOWED_HOSTS', default='localhost,127.0.0.1,*.railway.app', cast=Csv())

# ─── Application Definition ──────────────────────────────────────
INSTALLED_APPS: list[str] = [
    # Django built-in
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'corsheaders',
    'rest_framework_simplejwt',

    # Local apps
    'apps.core',
    'apps.users',
    'apps.subscriptions',
    'apps.payments',
    'apps.dashboard',
]

MIDDLEWARE: list[str] = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF: str = 'config.urls'

TEMPLATES: list[dict] = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ─── Database Configuration ──────────────────────────────────────
DB_ENGINE = config('DB_ENGINE', default='sqlite')

if DB_ENGINE == 'postgresql' or config('DATABASE_URL', default=None):
    DATABASES = {
        'default': dj_database_url.config(
            default=config('DATABASE_URL', default=''),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
    # Fallback to explicit env vars if DATABASE_URL is somehow not parsed correctly but vars are there
    if not DATABASES['default'].get('NAME'):
         DATABASES['default'] = {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='saas_db'),
            'USER': config('DB_USER', default='postgres'),
            'PASSWORD': config('DB_PASSWORD', default='postgres'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
        }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ─── Password Validation ─────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS: list[dict] = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─── Custom User Model ───────────────────────────────────────────
AUTH_USER_MODEL: str = 'users.CustomUser'

# ─── Internationalization ────────────────────────────────────────
LANGUAGE_CODE: str = 'en-us'
TIME_ZONE: str = 'UTC'
USE_I18N: bool = True
USE_TZ: bool = True

# ─── Static Files ────────────────────────────────────────────────
STATIC_URL: str = '/static/'
STATIC_ROOT: os.PathLike = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS: list[str] = [os.path.join(BASE_DIR, 'static')]
# Ensure the directory exists
os.makedirs(os.path.join(BASE_DIR, 'static'), exist_ok=True)

# WhiteNoise Configuration
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ─── Default Primary Key ─────────────────────────────────────────
DEFAULT_AUTO_FIELD: str = 'django.db.models.BigAutoField'

# ─── Django REST Framework ───────────────────────────────────────
REST_FRAMEWORK: dict = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# ─── SimpleJWT Configuration ─────────────────────────────────────
SIMPLE_JWT: dict = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# ─── CORS Configuration ──────────────────────────────────────────
CORS_ALLOWED_ORIGINS: list[str] = [
    config('FRONTEND_URL', default='http://localhost:3000'),
]
CORS_ALLOW_ALL_ORIGINS: bool = config('DJANGO_DEBUG', default=False, cast=bool)

# ─── Stripe Configuration ────────────────────────────────────────
STRIPE_SECRET_KEY: str = config('STRIPE_SECRET_KEY', default='')
STRIPE_PUBLIC_KEY: str = config('STRIPE_PUBLIC_KEY', default='')
STRIPE_WEBHOOK_SECRET: str = config('STRIPE_WEBHOOK_SECRET', default='')

# ─── Frontend URL ────────────────────────────────────────────────
FRONTEND_URL: str = config('FRONTEND_URL', default='http://localhost:3000')

# ─── Production Security Settings ──────────────────────────────────
if not DEBUG:
    SECURE_SSL_REDIRECT = config('DJANGO_SECURE_SSL_REDIRECT', default=True, cast=bool)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
