"""
KRISS DRILLING — Django settings
NOTE: Secrets here are kept as fallback so existing deployments keep working.
      Set them via environment variables in gunicorn.service to override.
"""
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Read from environment if set, otherwise fall back to existing values
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'cbd6ef6f3d4712b8db92b34f2da8d44fde92aa79584e5a9dd21cc045b8d7c8690c1ddb58e1276a3cc5330fdc52606a770543'
)

DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = ['192.168.0.250', '192.168.29.44', 'localhost', '127.0.0.1',
                 'db.krissdrilling.com', 'www.db.krissdrilling.com']
CSRF_TRUSTED_ORIGINS = ['https://db.krissdrilling.com']

# ── Security cookie flags (HTTPS is in front of gunicorn via Nginx) ──────────
SESSION_COOKIE_SECURE   = True
CSRF_COOKIE_SECURE      = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY    = True
SESSION_COOKIE_AGE      = 43200  # 12 hours

# Tell Django that requests behind Nginx with X-Forwarded-Proto are HTTPS
SECURE_PROXY_SSL_HEADER  = ('HTTP_X_FORWARDED_PROTO', 'https')

# Hardening — safe to enable now
SECURE_REFERRER_POLICY        = 'same-origin'
SECURE_CONTENT_TYPE_NOSNIFF   = True
X_FRAME_OPTIONS               = 'DENY'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'core',
    'ilm',
    'hsd',
    'masters',
    'pob',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE':       'django.db.backends.postgresql',
        'NAME':         os.environ.get('DB_NAME',     'rig_operations_py'),
        'USER':         os.environ.get('DB_USER',     'rig_user_py'),
        'PASSWORD':     os.environ.get('DB_PASSWORD', 'Eureka123'),
        'HOST':         os.environ.get('DB_HOST',     'localhost'),
        'PORT':         os.environ.get('DB_PORT',     '5432'),
        'CONN_MAX_AGE': 60,  # reuse DB connections — perf win, safe
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 6}},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'Asia/Kolkata'
USE_I18N      = True
USE_TZ        = True

STATIC_URL       = '/static/'
STATIC_ROOT      = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL           = '/login/'
LOGIN_REDIRECT_URL  = '/'
LOGOUT_REDIRECT_URL = '/login/'

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK          = 'bootstrap5'

COMPANY_NAME = 'KRISS DRILLING PVT. LTD.'

# ── Email Configuration ─────────────────────────────────────────────────────
EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = os.environ.get('EMAIL_HOST_USER',     'reports.krissdrilling@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'oswntdoxqmotfmys')
DEFAULT_FROM_EMAIL  = 'KRISS DRILLING Reports <reports.krissdrilling@gmail.com>'
REPORT_RECIPIENTS   = [
    'it.admin@krissdrilling.com',
    'head-operations@krissdrilling.com',
    'sankar.sengupta@krissdrilling.com',
    'rishi@krissdrilling.com',
    'kkn@cont-tech.com.sg',
    'bhaskar@krissdrilling.com',
    'contracts.coordination@krissdrilling.com',
]

# Make sure the logs directory exists
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# ── Logging — captures errors to a file so silent 500s become visible ───────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {'format': '{asctime} {levelname} {name} {message}', 'style': '{'},
    },
    'handlers': {
        'file': {
            'level':       'WARNING',
            'class':       'logging.handlers.RotatingFileHandler',
            'filename':    BASE_DIR / 'logs' / 'django.log',
            'maxBytes':    5 * 1024 * 1024,
            'backupCount': 5,
            'formatter':   'verbose',
        },
        'console': {'level': 'INFO', 'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'django': {'handlers': ['file', 'console'], 'level': 'INFO',  'propagate': True},
        'pob':    {'handlers': ['file', 'console'], 'level': 'INFO',  'propagate': False},
    },
}
