# encoding: utf-8
import os
import sys

# Add apps directory to sys.path
sys.path.insert(1, "%s/apps" % sys.path[0])

_configuration = os.environ.get('DJANGO_CONFIGURATION', 'prod').lower()

# Always set production settings
execfile('sherpa/conf/prod.py')
execfile('sherpa/conf/secret_prod.py')

# Override with development settings if running dev-configuration
if _configuration == 'dev':
    execfile('sherpa/conf/dev.py')
    execfile('sherpa/conf/secret_dev.py')

# Finally override with private settings if specified
try:
    execfile('sherpa/conf/private.py')
except IOError:
    pass
