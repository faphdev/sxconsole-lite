"""
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.

* * *

Django settings for sxconsole project.

Generated by 'django-admin startproject' using Django 1.8.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

import yaml
from django.core.urlresolvers import reverse_lazy
from django.template.base import add_to_builtins
from django.utils.translation import ugettext_lazy as _


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _check_permissions(path):
    if not os.path.isfile(path):
        return
    permissions = os.stat(path).st_mode
    assert oct(permissions)[-2:] == '00', (
        "Please make sure that this file is not "
        "accessible to other users: {}".format(path))

# Path to SX Console config file
_conf_path = os.path.join(BASE_DIR, 'conf.yaml')
_check_permissions(_conf_path)
with open(_conf_path) as f:
    _conf = yaml.safe_load(f)
    SERVER_CONF = _conf.get('server') or {}
    APP_CONF = _conf.get('app') or {}
    SX_CONF = _conf.get('sx') or {}
    EMAIL_CONF = _conf.get('mailing') or {}
    CARBON_CONF = _conf.get('carbon') or {}

# Customizations
_skin_name = _conf.get('skin', 'default')
_skin_path = os.path.join(BASE_DIR, 'skins', _skin_name, 'skin.yaml')
with open(_skin_path) as f:
    SKIN = yaml.safe_load(f)


def _path_from_config(key, default=None):
    """Return a path from config, with an optional default value.

    Relative paths are resolved in relation to `BASE_DIR`.
    """
    return os.path.join(BASE_DIR, SERVER_CONF.get(key, default))


def _as_list(value):
    """Ensure that the value is a list."""
    if not isinstance(value, list):
        value = [value]
    return value


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'jhy#v#c#_)i*h2bjcy5-%^kz0h=#c$r9wb_uie8vjj8n7qul@e'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = SERVER_CONF.get('debug', False)

# Enables demo mode
DEMO = SERVER_CONF.get('demo', False)

if DEMO:
    DEMO_USER = 'demo@skylable.com'
    DEMO_PASS = 'demo'

CSRF_COOKIE_SECURE = not DEBUG

if DEBUG:
    SESSION_COOKIE_NAME = 'sessionid_lite'
else:
    ALLOWED_HOSTS = _as_list(SERVER_CONF['hosts'])

# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_extensions',
    'sizefield',

    'sxconsole',
    'clusters',
    'accounts',
    'volumes',
    'users',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'sxconsole.middleware.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'sxconsole.middleware.ExtendSessionMiddleware',
    'sxconsole.middleware.ClusterConnectionMiddleware',
)

ROOT_URLCONF = 'sxconsole.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (os.path.join(BASE_DIR, 'templates'),),
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'sxconsole.context_processors.sx_console',
            ],
        },
    },
]

add_to_builtins('django.templatetags.i18n')

WSGI_APPLICATION = 'sxconsole.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': _path_from_config('db', 'db.sqlite3'),
    }
}
if 'sqlite' in DATABASES['default']['ENGINE']:
    _check_permissions(DATABASES['default']['NAME'])

# Server info
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')


# Sessions
SESSION_COOKIE_AGE = 60 * 60 * 24  # 1 day
SESSION_COOKIE_SECURE = not DEBUG
SESSION_EXPIRE_AT_BROWSER_CLOSE = True


# Auth stuff
AUTH_USER_MODEL = 'accounts.Admin'
LOGIN_URL = reverse_lazy('login')


# Mailing
EMAIL_HOST = EMAIL_CONF.get('host')
EMAIL_PORT = EMAIL_CONF.get('port')
EMAIL_HOST_USER = EMAIL_CONF.get('user')
EMAIL_HOST_PASSWORD = EMAIL_CONF.get('password')
EMAIL_USE_SSL = EMAIL_CONF.get('ssl')
EMAIL_USE_TLS = EMAIL_CONF.get('tls')
DEFAULT_FROM_EMAIL = EMAIL_CONF.get('from')

if DEMO:
    # Disable mailing in demo mode
    EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'


# Admin e-mails
SERVER_EMAIL = DEFAULT_FROM_EMAIL
ADMINS = APP_CONF.get('report_to')
if ADMINS:
    assert SERVER_EMAIL, "The 'mailing.from' field is required " \
        "if 'app.report_to' is given."
    ADMINS = [('Admin', email) for email in _as_list(ADMINS)]


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = APP_CONF.get('default_lang', 'en')

LANGUAGES = (
    ('en', _("English")),
    ('de', _("German")),
    ('it', _("Italian")),
    ('pl', _("Polish")),
)

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = (
    ('sxconsole', os.path.join(BASE_DIR, 'assets', 'build')),
    ('img', os.path.join(BASE_DIR, 'assets', 'img')),
)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
        },
        'file_django': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'django.log',
            'formatter': 'file_format',
            'maxBytes': 1024 ** 2,
            'backupCount': 1,
        },
        'file_sxconsole': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'sxconsole.log',
            'formatter': 'file_format',
            'maxBytes': 1024 ** 2,
            'backupCount': 1,
        },
        'file_api': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'api.log',
            'formatter': 'file_format',
            'maxBytes': 1024 ** 2,
            'backupCount': 1,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file_django', 'mail_admins'],
        },
        'sxconsole': {
            'handlers': ['console', 'file_sxconsole'],
        },
        'sxconsole.api': {
            'handlers': ['console', 'file_api'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
    'formatters': {
        'file_format': {
            'format': '\n%(levelname)s %(asctime)s\n%(message)s'
        },
    }
}

if DEBUG:
    _log_path = '.log/'
else:
    _log_path = '/srv/logs/'

for name in LOGGING['handlers']:
    if not name.startswith('file_'):
        continue
    handler = LOGGING['handlers'][name]
    handler['filename'] = os.path.join(_log_path, handler['filename'])
