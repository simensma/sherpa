# encoding: utf-8
# Django settings for Sherpa.
# See https://docs.djangoproject.com/en/1.4/ref/settings/

# Add apps directory to sys.path
import sys
sys.path.insert(1, "%s/apps" % sys.path[0][:sys.path[0].rfind('/')])

from sherpa.local_settings import *

ROOT_URLCONF = '' # Unused, but required
AUTH_PROFILE_MODULE = 'user.Profile'
LOGIN_URL = '/minside/logg-inn/'

AWS_ADS_PREFIX = 'ads/'
AWS_IMAGEGALLERY_PREFIX = 'images/'
AWS_BUCKET = 'cdn.turistforeningen.no'
AWS_BUCKET_SSL = 's3-eu-west-1.amazonaws.com/cdn.turistforeningen.no'
OLD_SITE = 'www2.turistforeningen.no'
BLOG_URL = 'blogg.turistforeningen.no'
BLOG_CATEGORY_API = 'api/get_category_index/'

# NETS URLs used for payment
NETS_REGISTER_URL = "https://epayment.bbs.no/Netaxept/Register.aspx"
NETS_TERMINAL_URL = "https://epayment.bbs.no/Terminal/default.aspx"
NETS_PROCESS_URL = "https://epayment.bbs.no/Netaxept/Process.aspx"

# For now, require only a minimum password length of 6. This might need to be reconsidered.
USER_PASSWORD_LENGTH = 6
RESTORE_PASSWORD_KEY_LENGTH = 40
RESTORE_PASSWORD_VALIDITY = 12 # Hours

# Pixel sizes for thumbnail images generated from uploaded images.
# Duplicated client-side in js/admin/editor/image-utils.js
THUMB_SIZES = [1880, 940, 500, 150]

MANAGERS = ADMINS = (
    ('Ali Kaafarani', 'ali@kvikshaug.no'),
    ('Håvard Eidheim', 'eidheim@live.no'),
)

DEFAULT_FROM_EMAIL = 'Den Norske Turistforening <no-reply@turistforeningen.no>'
SERVER_EMAIL = 'DNT Django <server-errors@turistforeningen.no>'

TIME_ZONE = 'Europe/Oslo'
LANGUAGE_CODE = 'nb' # See http://www.i18nguy.com/unicode/language-identifiers.html
USE_I18N = True
USE_L10N = True
STATIC_URL = '/static/'

DATABASE_ROUTERS = ['sherpa.db_routers.Router']

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'south', # Database migrations
    'focus', # Only db-models from Focus
    'core',
    'page',
    'admin',
    'analytics',
    'articles',
    'user',
    'enrollment',
    'association',
    'membership',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "sherpa.context_processors.menus",
    "sherpa.context_processors.current_site",
    "sherpa.context_processors.old_site",
)

MIDDLEWARE_CLASSES = (
    'sherpa.middleware.RedirectTrailingDot',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'sherpa.middleware.Sites',
    'sherpa.middleware.DecodeQueryString',
    # Use a monkeypatch for Djangos CommonMiddleware. See middleware.py for more info
    'sherpa.middleware.CommonMiddlewareMonkeypatched',
    #'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'sherpa.middleware.DeactivatedEnrollment',
)
