# encoding: utf-8
import os
import sys

# Add apps directory to sys.path
sys.path.insert(1, "%s/apps" % sys.path[0])

_configuration = os.environ.get('DJANGO_CONFIGURATION', 'dev').lower()

if _configuration == 'prod':
    from sherpa.conf.prod import *
    from sherpa.conf.secret_prod import *

elif _configuration == 'dev':
    from sherpa.conf.dev import *
    from sherpa.conf.secret_dev import *

# Private settings are optional
try:
    from sherpa.conf.private import *
except ImportError:
    pass
