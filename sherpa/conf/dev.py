# encoding: utf-8

# Extend and potentially override production settings
from .prod import *

TEMPLATE_DEBUG = DEBUG = True
INTERNAL_IPS = ('127.0.0.1',)

STATICFILES_DIRS = (
    "/sherpa/static",
)

CACHES = {
    'default': {
     'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
     'LOCATION': '127.0.0.1:11211',
    }
}

SENTRY_DSN = None # Deactivates Sentry

# Log everything to console, nothing to Sentry.
# Note: Sentry logs exceptions automatically, so it's not needed in 'root' or 'django'. Sentry also doesn't care
# about settings.DEBUG, so set SENTRY_DSN to None to deactivate it (require_debug_false won't work).
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(asctime)s\n%(message)s\n'
        },
        'verbose': {
            'format': '\n%(levelname)s (%(name)s) %(asctime)s\n%(pathname)s:%(lineno)d in %(funcName)s\n%(message)s\n'
        },
    },
    'filters': {
        'ignore_404': {
            '()': 'sherpa.log_filters.Ignore404'
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'sentry': {
            'level': 'DEBUG',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
            'filters': ['require_debug_false'],
        },
        # Optional file logging
        #'sherpa_file': {
        #    'level': 'DEBUG',
        #    'class': 'logging.FileHandler',
        #    'filename': '/logs/sherpa/sherpa.log',
        #    'formatter': 'verbose',
        #    'filters': ['ignore_404'],
        #},
        #'sentry_file': {
        #    'level': 'DEBUG',
        #    'class': 'logging.FileHandler',
        #    'filename': '/logs/sherpa/sentry.log',
        #    'formatter': 'verbose',
        #    'filters': ['ignore_404'],
        #},
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'sherpa': {
            'level': 'DEBUG',
            'handlers': ['sentry', 'console'],
            'propagate': False,
        },
        'django': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'django.db.backends': {
            # DEBUG prints all SQL-statements
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'boto': {
            # DEBUG is very verbose
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console'],
    },
}
