# encoding: utf-8
import multiprocessing
import os

# Server Socket
bind = ["0.0.0.0:8000"]

# Worker Processes
workers = multiprocessing.cpu_count() * 2 + 1

# When gevent gets their stuff together and release a version fixing the missing SSLv3 we can use
# gevent workers. Until then we are stuck with sync.
worker_class = "sync"

# We are allways behind a proxy so do not worry about who is forwarding.
forwarded_allow_ips = "*"

# Logging
accesslog = "/logs/sherpa/access.log"
errorlog = "/logs/sherpa/error.log"
loglevel = "info"

# Environment specific
_configuration = os.environ.get('DJANGO_CONFIGURATION', 'prod').lower()

if _configuration == 'dev':
    reload = True

if _configuration == 'prod':

    # Load application code before the worker processes are forked. By preloading an application
    # you can save some RAM resources as well as speed up server boot times. Although, if you defer
    # application loading to each worker process, you can reload your application code easily by
    # restarting workers.

    preload_app = True

