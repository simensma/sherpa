class Router(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'sherpa2':
            return 'sherpa-2'
        elif model._meta.app_label == 'focus':
            return 'focus'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'sherpa2':
            raise Exception("Don't write to this model!")
        elif model._meta.app_label == 'focus':
            if model._meta.object_name in ['Enrollment']:
                return 'focus'
            else:
                raise Exception("Don't write to this model!")
        return None

    def allow_syncdb(self, db, model):
        if model._meta.app_label in ['sherpa2', 'focus']:
            return False
        if db in ['sherpa-2', 'sherpa-2.5', 'focus']:
            return False
        return None
