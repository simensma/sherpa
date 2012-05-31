# Django settings for Sherpa.
# See https://docs.djangoproject.com/en/1.3/ref/settings/

from local_settings import *

ROOT_URLCONF = 'urls'
AUTH_PROFILE_MODULE='user.Profile'
LOGIN_URL = '/bruker/logg-inn/'

AWS_IMAGEGALLERY_PREFIX = 'images/'
AWS_BUCKET = 'cdn.turistforeningen.no'

MANAGERS = ADMINS = (
    ('Ali Kaafarani', 'ali@kvikshaug.no'),
)

TIME_ZONE = 'Europe/Oslo'
LANGUAGE_CODE = 'nb' # See http://www.i18nguy.com/unicode/language-identifiers.html
USE_I18N = True
USE_L10N = True
STATIC_URL = '/static/'

DATABASE_ROUTERS = ['db_routers.Router']

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
    'enrollment',
    'group',
    'memberservice',
    'membership',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'error.log'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins', 'file'],
            'level': 'DEBUG',
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
    "context_processors.menus"
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'middleware.Analytics',
    'middleware.Sites',
)
