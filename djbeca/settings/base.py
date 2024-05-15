# -*- coding: utf-8 -*-

"""Django settings for project."""

import os


# Debug
DEBUG = False
INFORMIX_DEBUG = ''
REQUIRED_ATTRIBUTE = True
ADMINS = ()
MANAGERS = ADMINS
SECRET_KEY = None
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Chicago'
TIME_INPUT_FORMATS = ('%H:%M %p',)
SITE_ID = 1
USE_I18N = False
USE_L10N = False
USE_TZ = False
DEFAULT_CHARSET = 'utf-8'
FILE_CHARSET = 'utf-8'
SERVER_URL = ''
DIRECTORY_API_URL = 'https://{0}/{1}'.format(SERVER_URL, 'directory/api/')
LIVEWHALE_API_URL = 'https://{0}'.format(SERVER_URL)
ROOT_URL = '/djbeca/'
ROOT_URLCONF = 'djbeca.core.urls'
WSGI_APPLICATION = 'djbeca.wsgi.application'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = BASE_DIR
PROJECT_APP = os.path.basename(BASE_DIR)
ROOT_URL = '/{0}/'.format(PROJECT_APP)
ADMIN_MEDIA_PREFIX = '/static/admin/'
MEDIA_ROOT = '{0}/assets/'.format(ROOT_DIR)
STATIC_ROOT = '{0}/static/'.format(ROOT_DIR)
STATIC_URL = '/static/{0}/'.format(PROJECT_APP)
MEDIA_URL = '/media/{0}/'.format(PROJECT_APP)
FILE_UPLOAD_PERMISSIONS = 0o644
STATICFILES_DIRS = ()
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
)
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
DATABASES = {
    'default': {
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'NAME': 'django_djbeca',
        'ENGINE': 'django.db.backends.mysql',
        'USER': '',
        'PASSWORD': '',
    },
    'workday': {
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'NAME': 'workday',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'workday',
        'PASSWORD': '',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'ssl': {
                'ca': '',
            },
        },
    },
}
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    # apps
    'djbeca.core',
    # needed for template tags
    'djtools',
    # gmail api for send mail
    'gmailapi_backend',
    # sign in as a user
    'loginas',
    # tagging package
    'taggit',
)
GRAPPELLI_ADMIN_TITLE = ''
MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)
# template stuff
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            '/data2/django_templates/djcher/',
            '/data2/django_templates/',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': [
                'djtools.context_processors.sitevars',
                'djbeca.context_processors.sitevars',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
# LDAP Constants
LDAP_SERVER = ''
LDAP_PORT = ''
LDAP_PROTOCOL = ''
LDAP_BASE = ''
LDAP_USER = ''
LDAP_PASS = None
LDAP_OBJECT_CLASS = ''
LDAP_GROUPS = None
LDAP_RETURN = ()
LDAP_ID_ATTR = ''
LDAP_AUTH_USER_PK = False
LDAP_EMAIL_DOMAIN = ''
LDAP_OBJECT_CLASS_LIST = []
LDAP_GROUPS = {}
LDAP_RETURN = []
LDAP_ID_ATTR = ''
LDAP_AUTH_USER_PK = False
# auth backends
AUTHENTICATION_BACKENDS = (
    'djauth.backends.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)
LOGIN_URL = '{0}accounts/login/'.format(ROOT_URL)
LOGOUT_URL = '{0}accounts/logout/'.format(ROOT_URL)
LOGIN_REDIRECT_URL = ROOT_URL
USE_X_FORWARDED_HOST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_DOMAIN = ''
SESSION_COOKIE_NAME = 'django_djbeca_cookie'
SESSION_COOKIE_AGE = 86400
# emails
DEFAULT_FROM_EMAIL = ''
SERVER_EMAIL = ''
SERVER_MAIL = ''
# gmail API settings
EMAIL_FROM = ''
GMAIL_USER = ''
EMAIL_BACKEND = 'gmailapi_backend.service.GmailApiBackend'
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.send']
GMAIL_SERVICE_ACCOUNT_JSON = ''
GOOGLE_SERVICE_ACCOUNT = ''
# security
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_SSL_REDIRECT = True
# REST API AUTHENTICATION TOKEN
REST_FRAMEWORK_TOKEN = ''
# OSP specific settings
OSP_GROUP = 'Sponsored Programs'
if DEBUG:
    PROPOSAL_EMAIL_LIST = []
else:
    PROPOSAL_EMAIL_LIST = []
# approval level positions
PROVOST_GROUP = 'Provost'
CFO_GROUP = 'CFO'
PRESIDENT_GROUP = 'President'
# logging
LOG_FILEPATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs/')
LOG_FILENAME = '{0}{1}'.format(LOG_FILEPATH, 'debug.log')
DEBUG_LOG_FILENAME = '{0}{1}'.format(LOG_FILEPATH, 'debug.log')
INFO_LOG_FILENAME = '{0}{1}'.format(LOG_FILEPATH, 'info.log')
ERROR_LOG_FILENAME = '{0}{1}'.format(LOG_FILEPATH, 'error.log')
CUSTOM_LOG_FILENAME = '{0}{1}'.format(LOG_FILEPATH, 'custom.log')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format' : '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s',
            'datefmt' : '%Y/%b/%d %H:%M:%S'
        },
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
            'datefmt' : '%Y/%b/%d %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'logfile': {
            'level':'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOG_FILENAME,
            'formatter': 'standard',
        },
        'console':{
            'level':'INFO',
            'class':'logging.StreamHandler',
            'formatter': 'standard'
        },
        'mail_admins': {
            'level': 'ERROR',
            'include_html': True,
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'custom_logfile': {
            'level':'ERROR',
            'filters': ['require_debug_true'], # do not run error logger in production
            'class': 'logging.FileHandler',
            'filename': CUSTOM_LOG_FILENAME,
            'formatter': 'custom',
        },
        'info_logfile': {
            'level':'INFO',
            'class':'logging.handlers.RotatingFileHandler',
            'backupCount': 10,
            'maxBytes': 50000,
            'filters': ['require_debug_false'], # run logger in production
            'filename': INFO_LOG_FILENAME,
            'formatter': 'simple',
        },
        'debug_logfile': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': DEBUG_LOG_FILENAME,
            'handlers':['logfile'],
            'formatter': 'verbose'
        },
        'error_logfile': {
            'level': 'ERROR',
            'filters': ['require_debug_true'], # do not run error logger in production
            'class': 'logging.FileHandler',
            'filename': ERROR_LOG_FILENAME,
            'formatter': 'verbose'
        },
        'redpanda': {
            'handlers':['logfile'],
            'propagate': True,
            'level':'DEBUG',
        },
        'redpanda.lynx': {
            'handlers':['logfile'],
            'propagate': True,
            'level':'DEBUG',
        },
        'redpanda.core': {
            'handlers':['logfile'],
            'propagate': True,
            'level':'DEBUG',
        },
        'django': {
            'handlers':['console'],
            'propagate': True,
            'level':'WARN',
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


##################
# LOCAL SETTINGS #
##################

# Allow any settings to be defined in local.py which should be
# ignored in your version control system allowing for settings to be
# defined per machine.

# Instead of doing "from .local import *", we use exec so that
# local has full access to everything defined in this module.
# Also force into sys.modules so it's visible to Django's autoreload.

phile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'local.py')
if os.path.exists(phile):
    import imp
    import sys
    module_name = '{0}.settings.local'.format(PROJECT_APP)
    module = imp.new_module(module_name)
    module.__file__ = phile
    sys.modules[module_name] = module
    exec(open(phile, 'rb').read())
