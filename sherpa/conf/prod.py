# encoding: utf-8
from datetime import datetime, date

ROOT_URLCONF = 'sherpa.urls_central' # Should be overridden from the Sites middleware in almost all cases, but not when raising PermissionDenied in other middleware.
AUTH_USER_MODEL = 'user.User'
LOGIN_URL = '/minside/logg-inn/'

AWS_ADS_PREFIX = 'ads/'
AWS_IMAGEGALLERY_PREFIX = 'images/'
AWS_FJELLTREFFEN_IMAGES_PREFIX = 'fjelltreffen'
AWS_PUBLICATIONS_PREFIX = 'publications'
AWS_CAMPAIGNS_PREFIX = 'campaigns'
AWS_FILEUPLOAD_PREFIX = 'files'
AWS_BUCKET = 'cdn.turistforeningen.no'
AWS_BUCKET_SSL = 's3-eu-west-1.amazonaws.com/cdn.turistforeningen.no'
AWS_BUCKET_DEV = 'dev.cdn.turistforeningen.no'
AWS_BUCKET_SSL_DEV = 's3-eu-west-1.amazonaws.com/dev.cdn.turistforeningen.no'
OLD_SITE = 'www2.turistforeningen.no'
INSTAGRAM_CLIENT_ID = '9f849b1f6e97480ea58ee989159a597a'
DEBUG_ANALYTICS_UA = 'UA-266436-62'

# Our SMS-service endpoint
SMS_URL = "http://admin.telefonkatalogen.no/smsgateway/sendSms?sender=DNT&targetNumbers=%s&sms=%s"
SMS_RESTRICTION_WHITELIST = ['212.71.74.98'] # DNT administrations current public IP address (for memberservice)

# NETS URLs used for payment
NETS_REGISTER_URL = "https://epayment.bbs.no/Netaxept/Register.aspx"
NETS_TERMINAL_URL = "https://epayment.bbs.no/Terminal/default.aspx"
NETS_PROCESS_URL = "https://epayment.bbs.no/Netaxept/Process.aspx"
NETS_QUERY_URL = "https://epayment.bbs.no/Netaxept/Query.aspx"

DNTOSLO_MONTIS_API_URL = "https://booking.dntoslo.no/api/turer"

# DIBS endpoints
DIBS_ENDPOINT = "https://payment.dibspayment.com/dpw/entrypoint"

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
FJELLTREFFEN_BULK_COUNT = 20 # Annonser to load when a user requests more
FJELLTREFFEN_IMAGE_THUMB_SIZE = 150 # Max pixel width and/or height
ADMIN_USER_SEARCH_CHAR_LENGTH = 4
DATABASE_CONNECTION_TIMEOUT = 10 # seconds

MSSQL_MAX_PARAMETER_COUNT = 2000 # Actually 2100, but leave room for some other parameters

# Emails to DNT Medlemsservice
MEMBERSERVICE_EMAIL = 'DNT Medlemsservice <medlem@turistforeningen.no>'

# Define when årskravet is performed each year.
# We may need to know when the *previous* years årskrav started, so keep a history.
#
# initiation_date: When årskravet is started, usually the same time as when card payment
#   is deactivated. From this date, only invoices are accepted and they will be enrolled
#   for the *next* year.
#
# actual_date: The actual date årskravet is performed. Can be a few days earlier than the
#   public date, we need to know this because this is the day the prices are updated
#   IMPORTANT: This should be set to the day *FOLLOWING* the day årskravet is performed,
#   since checks will change the UI on the *specified* date.
#
# public_date: The publicly displayed date - members are informed that after this date,
#   enrollments are valid for the next year as well. Usually the first of some month.
#
# A new entry needs to be created each year, but if forgotten/delayed, an entry will be
# faked with the dates of the previous year. See core.util.membership_year_start
MEMBERSHIP_YEAR_START = [
    {
        'initiation_date': date(year=2012, month=9, day=30),
        'actual_date': date(year=2012, month=10, day=1),
        'public_date': date(year=2012, month=10, day=1),
    },
    {
        'initiation_date': date(year=2013, month=10, day=20),
        'actual_date': date(year=2013, month=10, day=25), # Note that this is one day *after*
        'public_date': date(year=2013, month=11, day=1),
    },
    {
        'initiation_date': date(year=2014, month=10, day=13),
        # actual_date was vaguely specified by memberservice this year; might occur a day or two before this date
        'actual_date': date(year=2014, month=10, day=16),
        'public_date': date(year=2014, month=11, day=1),
    },
]

# Pixel sizes for thumbnail images generated from uploaded images.
THUMB_SIZES = [1880, 940, 500, 150]

# Map column count to their minimum size. This will need to be changed if:
# - The number of available columns in the admin editor changes
# - The grid layout (column width) in the design changes
COLUMN_SPAN_MAP = {
    4: 220,
    3: 300,
    2: 460,
    1: 940,
}

# Require this many characters for an image search
IMAGE_SEARCH_LENGTH = 3

# Whenever Focus goes down, add the period here.
# Note that it's not always obvious which apps/services require Focus, try to account for
# all of them in the context processor/middleware that checks this setting.
FOCUS_DOWNTIME_PERIODS = [
    {
        'from': datetime(year=2013, month=4, day=17, hour=16),
        'to': datetime(year=2013, month=4, day=17, hour=21),
        'period_message': 'torsdag 17. april fra kl. 16:00 til kl. 21:00'
    },
    {
        'from': datetime(year=2013, month=6, day=25, hour=17),
        'to': datetime(year=2013, month=6, day=25, hour=20),
        'period_message': 'tirsdag 25. juni fra kl. 17:00 og ut kvelden'
    },
    {
        'from': datetime(year=2013, month=9, day=6, hour=19),
        'to': datetime(year=2013, month=9, day=6, hour=21),
        'period_message': 'i korte perioder fredag kveld 6. september'
    },
    {
        'from': datetime(year=2013, month=10, day=22, hour=17),
        'to': datetime(year=2013, month=10, day=22, hour=18),
        'period_message': 'tirsdag 22. oktober fra kl. 17:00 til kl. 18:00'
    },
    {
        'from': datetime(year=2013, month=10, day=24, hour=23),
        'to': datetime(year=2013, month=10, day=25, hour=4),
        'period_message': 'natt til fredag 25. oktober, til ca. kl. 04:00'
    },
    {
        'from': datetime(year=2013, month=11, day=26, hour=17),
        'to': datetime(year=2013, month=11, day=26, hour=23),
        'period_message': 'tirsdag 26. november fra kl. 17:00 og ut kvelden'
    },
    {
        'from': datetime(year=2013, month=12, day=1, hour=9),
        'to': datetime(year=2013, month=12, day=1, hour=14),
        'period_message': 'søndag 1. desember fra kl. 09:00 til kl. 14:00'
    },
    {
        'from': datetime(year=2013, month=12, day=3, hour=20),
        'to': datetime(year=2013, month=12, day=3, hour=21),
        'period_message': 'en times tid i kveld, til kl. 21:00'
    },
    {
        'from': datetime(year=2013, month=12, day=15, hour=8),
        'to': datetime(year=2013, month=12, day=15, hour=12),
        'period_message': 'denne morgenen, til kl. 12:00'
    },
    {
        'from': datetime(year=2013, month=12, day=19, hour=18),
        'to': datetime(year=2013, month=12, day=19, hour=18, minute=20),
        'period_message': 'et kvarters tid rundt klokken 6 i kveld'
    },
    {
        'from': datetime(year=2014, month=2, day=7, hour=17),
        'to': datetime(year=2014, month=2, day=9, hour=17),
        'period_message': 'mesteparten av helgen'
    },
    {
        'from': datetime(year=2014, month=3, day=5, hour=17),
        'to': datetime(year=2014, month=3, day=5, hour=23, minute=59),
        'period_message': 'onsdag 5. mars fra kl. 17:00 og utover kvelden'
    },
    {
        'from': datetime(year=2014, month=4, day=7, hour=17),
        'to': datetime(year=2014, month=4, day=7, hour=19),
        'period_message': 'mandag 7. april fra kl. 17:00 til kl. 19:00'
    },
    {
        'from': datetime(year=2014, month=5, day=5, hour=0),
        'to': datetime(year=2014, month=5, day=5, hour=6),
        'period_message': 'i natt frem til kl. 06:00'
    },
    {
        'from': datetime(year=2014, month=5, day=14, hour=18),
        'to': datetime(year=2014, month=5, day=14, hour=19),
        'period_message': 'i kveld mellom kl. 18 og 19'
    },
    {
        'from': datetime(year=2014, month=10, day=15, hour=14),
        'to': datetime(year=2014, month=10, day=17, hour=10),
        'period_message': 'til og med fredag'
    },
    {
        'from': datetime(year=2014, month=11, day=5, hour=16),
        'to': datetime(year=2014, month=11, day=5, hour=18),
        'period_message': 'et par timer i kveld'
    },
]

DEFAULT_FROM_EMAIL = 'Den Norske Turistforening <no-reply@turistforeningen.no>'
SERVER_EMAIL = 'DNT Django <server-errors@turistforeningen.no>'

TIME_ZONE = 'Europe/Oslo'
LANGUAGE_CODE = 'nb' # See http://www.i18nguy.com/unicode/language-identifiers.html
USE_I18N = True
USE_L10N = True
STATIC_URL = '/static/'

EDITOR_PLACEHOLDER_IMAGE = '%simg/admin/sites/editor/placeholder.png' % STATIC_URL

DATABASE_ROUTERS = ['sherpa.db_routers.Router']
AUTHENTICATION_BACKENDS = ('sherpa.auth_backends.CustomBackend',)

# CORS settings - allow all origins given a request to the specified URLs
CORS_URLS_REGEX = r'^/(api|ekstern-betaling|o/token)/.*$'
CORS_ALLOW_METHODS = ('GET', 'POST')
CORS_ORIGIN_ALLOW_ALL = True

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis', # GeoDjango

    'raven.contrib.django', # Error logging
    'captcha', # django-recaptcha
    'mptt', # Modified Preorder Tree Traversal - see https://django-mptt.github.io/django-mptt/
    'oauth2_provider', # django-oauth-toolkit - see https://django-oauth-toolkit.readthedocs.org/
    'corsheaders', # django-cors-headers - see https://pypi.python.org/pypi/django-cors-headers/

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
    'foreninger',
    'membership',
    'instagram',
    'fjelltreffen',
    'conditions',
    'aktiviteter',
    'connect',
    'api',
    'fotokonkurranse',
    'turbasen',
    'montis',
    'payment',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    "sherpa.context_processors.menus",
    "sherpa.context_processors.main_site",
    "sherpa.context_processors.current_site",
    "sherpa.context_processors.old_site",
    "sherpa.context_processors.admin_active_forening",
    "sherpa.context_processors.db_connections",
    "sherpa.context_processors.dntconnect",
    "sherpa.context_processors.membership_year_start",
    "sherpa.context_processors.do_not_track",
    "sherpa.context_processors.current_time",
    "sherpa.context_processors.analytics_ua",
    "sherpa.context_processors.s3_bucket",
    "sherpa.context_processors.editor_placeholder_image",
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'sherpa.middleware.TemporaryCorsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'sherpa.middleware.Redirect',
    'sherpa.middleware.DBConnection',
    'sherpa.middleware.DefaultLanguage',
    'sherpa.middleware.Sites',
    'sherpa.middleware.CurrentApp',
    'sherpa.middleware.DecodeQueryString',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'sherpa.middleware.ChangeActiveForening',
    'sherpa.middleware.ActiveForening',
    'sherpa.middleware.CheckOauth2ApplicationsPermission',
    'sherpa.middleware.CheckSherpaPermissions',
    'sherpa.middleware.DeactivatedEnrollment',
    'sherpa.middleware.FocusDowntime',
    'sherpa.middleware.ActorDoesNotExist',
)

TEMPLATE_DEBUG = DEBUG = False

TEMPLATE_DIRS = (
    "/sherpa/templates",
)

LOCALE_PATHS = (
    "/sherpa/locale",
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

RAVEN_CONFIG = {
    'string_max_length': 100000
}

# Note: sentry automatically logs uncaught exceptions, so there's
# no need to add it to the 'root' or 'django' loggers
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(asctime)s\n%(message)s\n'
        },
        'verbose': {
            'format': '%(levelname)s (%(name)s) %(asctime)s\n%(pathname)s:%(lineno)d in %(funcName)s\n%(message)s\n'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'ignore_404': {
            '()': 'sherpa.log_filters.Ignore404'
        }
    },
    'handlers': {
        'sentry': {
            'level': 'DEBUG',
            'class': 'raven.contrib.django.handlers.SentryHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
            'filters': ['require_debug_false'],
        },
        'sherpa_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/logs/sherpa/sherpa.log',
            'formatter': 'verbose',
            'filters': ['ignore_404'],
        },
        'sentry_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/logs/sherpa/sentry.log',
            'formatter': 'verbose',
            'filters': ['ignore_404'],
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'sherpa': {
            'handlers': ['sentry', 'sherpa_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django': {
            'level': 'DEBUG',
            'handlers': ['sherpa_file'],
            'propagate': False,
        },
        'boto': {
            # DEBUG is very verbose
            'level': 'INFO',
            'handlers': ['sherpa_file'],
            'propagate': False,
        },
        'sentry': {
           'level': 'DEBUG',
           'handlers': ['sentry_file'],
           'propagate': False,
        },
        'raven': {
           'level': 'DEBUG',
           'handlers': ['sentry_file'],
           'propagate': False,
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['sherpa_file'],
    }
}
