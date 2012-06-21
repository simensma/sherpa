# Django settings for Sherpa.
# See https://docs.djangoproject.com/en/1.3/ref/settings/

from local_settings import *

ROOT_URLCONF = 'urls'
AUTH_PROFILE_MODULE='user.Profile'
LOGIN_URL = '/minside/logg-inn/'

AWS_ADS_PREFIX = 'ads/'
AWS_IMAGEGALLERY_PREFIX = 'images/'
AWS_BUCKET = 'cdn.turistforeningen.no'
AWS_BUCKET_SSL = 's3-eu-west-1.amazonaws.com/cdn.turistforeningen.no'
OLD_SITE = 'www2.turistforeningen.no'

# For now, require only a minimum password length of 6. This might need to be reconsidered.
USER_PASSWORD_LENGTH = 6
RESTORE_PASSWORD_KEY_LENGTH = 40
RESTORE_PASSWORD_VALIDITY = 12 # Hours

MANAGERS = ADMINS = (
    ('Ali Kaafarani', 'ali@kvikshaug.no'),
)

DEFAULT_FROM_EMAIL = 'Den Norske Turistforening <no-reply@turistforeningen.no>'
SERVER_EMAIL = 'DNT Django <server-errors@turistforeningen.no>'

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
    "context_processors.menus",
    "context_processors.old_site",
    "context_processors.first_visit"
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'middleware.RedirectTrailingDot',
    'middleware.Analytics',
    'middleware.Sites',
)
