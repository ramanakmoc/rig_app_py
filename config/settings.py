from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'insecure-development-key-change-me')

DEBUG = False

ALLOWED_HOSTS = ['192.168.0.250', '192.168.29.44', 'localhost', '127.0.0.1', 'db.krissdrilling.com', 'www.db.krissdrilling.com']
CSRF_TRUSTED_ORIGINS = ['https://db.krissdrilling.com']
#SESSION_COOKIE_SECURE = True
#CSRF_COOKIE_SECURE = True

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
    'email_reports',
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
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'rig_operations_py'),
        'USER': os.environ.get('DB_USER', 'rig_user_py'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 6}},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']


MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL           = '/login/'
LOGIN_REDIRECT_URL  = '/'
LOGOUT_REDIRECT_URL = '/login/'

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 43200  # 12 hours

CSRF_COOKIE_HTTPONLY = True

COMPANY_NAME = 'KRISS DRILLING PVT. LTD.'

# Email Configuration
EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL  = os.environ.get('DEFAULT_FROM_EMAIL', 'KRISS DRILLING Reports <reports@localhost>')
REPORT_RECIPIENTS   = [item.strip() for item in os.environ.get('REPORT_RECIPIENTS', '').split(',') if item.strip()]

# Automated email report collection
EMAIL_COLLECTION_FERNET_KEY = os.environ.get('EMAIL_COLLECTION_FERNET_KEY', '')
EMAIL_COLLECTION_ALERT_RECIPIENTS = [
    item.strip() for item in os.environ.get('EMAIL_COLLECTION_ALERT_RECIPIENTS', '').split(',') if item.strip()
]
EMAIL_COLLECTION_MAX_ATTACHMENT_BYTES = int(os.environ.get('EMAIL_COLLECTION_MAX_ATTACHMENT_BYTES', 25 * 1024 * 1024))
EMAIL_COLLECTION_MAX_ZIP_MEMBERS = int(os.environ.get('EMAIL_COLLECTION_MAX_ZIP_MEMBERS', 50))
EMAIL_COLLECTION_MAX_ZIP_UNCOMPRESSED_BYTES = int(
    os.environ.get('EMAIL_COLLECTION_MAX_ZIP_UNCOMPRESSED_BYTES', 100 * 1024 * 1024)
)
EMAIL_COLLECTION_REVIEW_THRESHOLD = float(os.environ.get('EMAIL_COLLECTION_REVIEW_THRESHOLD', '0.65'))
EMAIL_COLLECTION_MAX_ATTEMPTS = int(os.environ.get('EMAIL_COLLECTION_MAX_ATTEMPTS', 3))
EMAIL_REPORTS_AI_EXTRACTOR = os.environ.get('EMAIL_REPORTS_AI_EXTRACTOR', '')
