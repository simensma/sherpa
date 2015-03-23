# encoding: utf-8
import os
import sys

# Add apps directory to sys.path
sys.path.insert(1, "%s/apps" % sys.path[0])

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

_configuration = os.environ.get('DJANGO_CONFIGURATION', 'prod').lower()

# Always set production settings
execfile('%s/sherpa/conf/prod.py' % BASE_DIR)
execfile('%s/private-data/conf/prod.py' % BASE_DIR)

# Override with staging settings
# This should only unset secret stuff, not the behaviour!
if _configuration == 'staging':
    execfile('%s/private-data/conf/staging.py' % BASE_DIR)

# Override with development settings if running dev-configuration
if _configuration == 'dev':
    execfile('%s/sherpa/conf/dev.py' % BASE_DIR)
    execfile('%s/private-data/conf/dev.py' % BASE_DIR)

# Finally override with private settings if specified
try:
    execfile('%s/sherpa/conf/private.py' % BASE_DIR)
except IOError:
    pass
