# Django settings for Sherpa 3.
# See https://docs.djangoproject.com/en/1.3/ref/settings/

from local_settings import *

SITE_ID = 1
ROOT_URLCONF = 'urls'
AUTH_PROFILE_MODULE='user.Profile'
LOGIN_URL = '/bruker/logg-inn/'

AWS_IMAGEGALLERY_PREFIX = 'images/'
AWS_BUCKET = 'cdn.turistforeningen.no'

MANAGERS = ADMINS = (
    ('Ali Kaafarani', 'ali.kaafarani@turistforeningen.no'),
)

TIME_ZONE = 'Europe/Oslo'
LANGUAGE_CODE = 'nb' # See http://www.i18nguy.com/unicode/language-identifiers.html
USE_I18N = False
USE_L10N = True
STATIC_URL = '/static/'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'south', # Database migrations
    'page',
    'admin',
    'analytics',
    'articles',
    'user',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "context_processors.sql_queries"
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'middleware.Analytics',
)
