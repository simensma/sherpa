class Router(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'group':
            return 'sherpa-2'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'group':
            raise Exception("Don't write to this model!")
        return None

    def allow_syncdb(self, db, model):
        if db in ['sherpa-2', 'sherpa-2.5']:
            return False
        return None
