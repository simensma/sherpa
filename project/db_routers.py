class Router(object):
    def db_for_read(self, model, **hints):
        return None

    def db_for_write(self, model, **hints):
        return None

    def allow_syncdb(self, db, model):
        if db == 'sherpa-2' or db == 'sherpa-2.5':
            return False
        return None
