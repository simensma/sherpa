# encoding: utf-8
# Django settings for Sherpa.
# See https://docs.djangoproject.com/en/1.4/ref/settings/

# Add apps directory to sys.path
import sys
sys.path.insert(1, "%s/apps" % sys.path[0][:sys.path[0].rfind('/')])

from sherpa.local_settings import *

ROOT_URLCONF = 'sherpa.urls_main' # Should be overridden from the Sites middleware in almost all cases, but not when raising PermissionDenied in other middleware.
AUTH_PROFILE_MODULE = 'user.Profile'
LOGIN_URL = '/minside/logg-inn/'

AWS_ADS_PREFIX = 'ads/'
AWS_IMAGEGALLERY_PREFIX = 'images/'
AWS_FJELLTREFFEN_IMAGES_PREFIX = 'fjelltreffen'
AWS_BUCKET = 'cdn.turistforeningen.no'
AWS_BUCKET_SSL = 's3-eu-west-1.amazonaws.com/cdn.turistforeningen.no'
OLD_SITE = 'www2.turistforeningen.no'
BLOG_URL = 'blogg.turistforeningen.no'
BLOG_CATEGORY_API = 'api/get_category_index/'
INSTAGRAM_CLIENT_ID = '9f849b1f6e97480ea58ee989159a597a'

# Our SMS-service endpoint
SMS_URL = "https://bedrift.telefonkatalogen.no/tk/sendsms.php?charset=utf-8&cellular=%s&msg=%s"

# NETS URLs used for payment
NETS_REGISTER_URL = "https://epayment.bbs.no/Netaxept/Register.aspx"
NETS_TERMINAL_URL = "https://epayment.bbs.no/Terminal/default.aspx"
NETS_PROCESS_URL = "https://epayment.bbs.no/Netaxept/Process.aspx"

# For now, require only a minimum password length of 6. This might need to be reconsidered.
USER_PASSWORD_LENGTH = 6
RESTORE_PASSWORD_KEY_LENGTH = 40
RESTORE_PASSWORD_VALIDITY = 12 # Hours
MEMBERID_LOOKUPS_LIMIT = 15 # Amount of allowed memberid + zipcode lookups when registering for user page
MEMBERID_LOOKUPS_BAN = 60 * 60 * 4 # Amount of seconds the ban should last when exceeding lookup limit
FOCUS_MEMBER_CACHE_PERIOD = 60 * 60 # Caching of memberdata (Actor, Services)
FJELLTREFFEN_ANNONSE_RETENTION_DAYS = 90 # How long fjelltreffen-annonser are shown after creation
FJELLTREFFEN_AGE_LIMITS = [18, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80] # Age queries are rounded to these values
FJELLTREFFEN_AGE_LIMIT = min(FJELLTREFFEN_AGE_LIMITS)
FJELLTREFFEN_REPORT_EMAIL = 'DNT medlemsservice <medlem@turistforeningen.no>'
FJELLTREFFEN_BULKLOADNUM = 20 #annonser to load when a user requests more
FJELLTREFFEN_IMAGE_THUMB_SIZE = 150 # Max pixel width and/or height
CAPTCHA_FLITE_PATH = '/usr/bin/flite'
CAPTCHA_FONT_SIZE = 50
CAPTCHA_OUTPUT_FORMAT = '<p>%(image)s %(hidden_field)s</p><p>%(text_field)s</p>'



# From the start of this month, memberships are for the remaining year AND next year
# (1 = January, 12 = December)
MEMBERSHIP_YEAR_START = 10

# Pixel sizes for thumbnail images generated from uploaded images.
# Duplicated client-side in js/admin/editor/image-utils.js
THUMB_SIZES = [1880, 940, 500, 150]

# Require this many characters for an image search
IMAGE_SEARCH_LENGTH = 3

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
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'raven.contrib.django', # Error logging
    'captcha', # django-simple-captcha
    'south', # Database migrations
    'focus', # Only db-models from Focus
    'sherpa2', # Only db-models from Sherpa 2
    'sherpa25', # Only db-models from Sherpa 2.5
    'core',
    'page',
    'admin',
    'analytics',
    'articles',
    'user',
    'enrollment',
    'association',
    'membership',
    'instagram',
    'fjelltreffen',
    'conditions',
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
    "sherpa.context_processors.admin_user_associations",
)

MIDDLEWARE_CLASSES = (
    'sherpa.middleware.RedirectTrailingDot',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'sherpa.middleware.Sites',
    'sherpa.middleware.CurrentApp',
    'sherpa.middleware.DecodeQueryString',
    # Use a monkeypatch for Djangos CommonMiddleware. See middleware.py for more info
    'sherpa.middleware.CommonMiddlewareMonkeypatched',
    #'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'sherpa.middleware.SetActiveAssociation',
    'sherpa.middleware.CheckSherpaPermissions',
    'sherpa.middleware.DeactivatedEnrollment',
)
