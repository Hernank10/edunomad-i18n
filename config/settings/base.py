import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = 'django-insecure-nomad-key-test'
DEBUG = True
ALLOWED_HOSTS = ['*']

LANGUAGE_CODE = 'es-co'

LANGUAGES = [
    ('es',      _('Español')),
    ('en',      _('English')),
    ('pt',      _('Português')),
    ('fr',      _('Français')),
    ('de',      _('Deutsch')),
    ('it',      _('Italiano')),
    ('zh-hans', _('中文 (简体)')),
    ('ja',      _('日本語')),
    ('ko',      _('한국어')),
    ('ar',      _('العربية')),
    ('hi',      _('हिन्दी')),
    ('ru',      _('Русский')),
    ('nl',      _('Nederlands')),
    ('tr',      _('Türkçe')),
    ('pl',      _('Polski')),
    ('sv',      _('Svenska')),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.core',
    'apps.subscription',
    'apps.generator',
    'apps.language_practice',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
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
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

USE_I18N = True
