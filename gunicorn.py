# encoding: utf-8
import multiprocessing
import os

# Server Socket
bind = ["0.0.0.0:8000"]

# When gevent gets their stuff together and release a version fixing the missing
# SSLv3 we can use gevent workers. Until then we are stuck with sync.
worker_class = "sync"

# We are allways behind a proxy so do not worry about who is forwarding.
forwarded_allow_ips = "*"

# Environment specific
_configuration = os.environ.get('DJANGO_CONFIGURATION', 'prod').lower()

if _configuration == 'dev':
    loglevel = "info"
    accesslog = "-"     # “-” means log to stderr
    errorlog = "-"      # “-” means log to stderr

    # Restart workers when code changes.
    reload = True

if _configuration == 'prod':
    loglevel = "warn"
    accesslog = None    # "/logs/sherpa/access.log"
    errorlog = "/logs/sherpa/error.log"

    # http://gunicorn-docs.readthedocs.org/en/latest/design.html#how-many-workers

    # Using threads instead of processes is a good way to reduce the memory
    # footprint of Gunicorn, while still allowing for application upgrades using
    # the reload signal, as the application code will be shared among workers
    # but loaded only in the worker processes (unlike when using the preload
    # setting, which loads the code in the master process).
    workers = multiprocessing.cpu_count() # * 2 + 1

    # Run each worker with the specified number of threads.
    threads = 2

    # worker_connections = 1000
    # max_requests = 0
    # max_requests_jitter = 0
    # timeout = 30
    # graceful_timeout = 30
    # keepalive = 2

    # Load application code before the worker processes are forked. By
    # preloading an application you can save some RAM resources as well as speed
    # up server boot times.
    preload_app = True

    # syslog
    # statsd
