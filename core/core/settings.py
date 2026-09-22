import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-miroha-monolith-heritage-key-2026'

# Включаем DEBUG = True для безопасной отладки и вывода дизайна без 400 ошибок
DEBUG = True

ALLOWED_HOSTS = ['*', 'miroha.ru', 'www.miroha.ru', '89.111.155.234', '185.182.110.96', '127.0.0.1', 'localhost']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storage_control',
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

ROOT_URLCONF = 'core.urls'
WSGI_APPLICATION = 'core.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "storage_control", "templates")],
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

# 🌐 ВОЗВРАЩАЕМ ПРОМЫШЛЕННЫЙ ENTERPRISE POSTGRESQL НА СКВОЗНОМ ПРИВАТНОМ IP
DATABASES = {
    'default': {
        'BACKEND': 'django.db.backends.postgresql',
        'NAME': 'miroha_db',
        'USER': 'maxim_admin',
        'PASSWORD': 'MirohaCryptoPostgres2026',
        'HOST': '192.168.0.231',
        'PORT': '5432',
    }
}

# КРИТИЧЕСКИЙ DevOps-МОСТ СИНХРОНИЗАЦИИ С NGINX БЕЗ ОШИБОК 400
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Полное отключение редиректов и петель безопасности (Открытый HTTP эфир)
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/miroha_static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
