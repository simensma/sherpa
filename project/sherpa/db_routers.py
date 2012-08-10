class Router(object):
    def db_for_read(self, model, **hints):
        if model._meta.object_name == 'Association':
            return 'sherpa-2'
        elif model._meta.object_name in ['Enrollment', 'Actor', 'ActorAddress', 'FocusZipcode', 'Price']:
            return 'focus'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.object_name in ['Association', 'Actor', 'ActorAddress', 'FocusZipcode', 'Price']:
            raise Exception("Don't write to this model!")
        elif model._meta.object_name in ['Enrollment']:
            return 'focus'
        return None

    def allow_syncdb(self, db, model):
        if model._meta.object_name in ['Association', 'Enrollment', 'Actor', 'ActorAddress', 'FocusZipcode', 'Price']:
            return False
        if db in ['sherpa-2', 'sherpa-2.5', 'focus']:
            return False
        return None
