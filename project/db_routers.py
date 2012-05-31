class Router(object):
    def db_for_read(self, model, **hints):
        if model._meta.object_name == 'Group':
            return 'sherpa-2'
        elif model._meta.object_name in ['FocusUser', 'FocusActType', 'Actor', 'ActorAddress', 'FocusZipcode']:
            return 'focus'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.object_name in ['Group', 'Actor', 'ActorAddress', 'FocusZipcode']:
            raise Exception("Don't write to this model!")
        elif model._meta.object_name in ['FocusUser', 'FocusActType']:
            return 'focus'
        return None

    def allow_syncdb(self, db, model):
        if model._meta.object_name in ['Group', 'FocusUser', 'FocusActType', 'Actor', 'ActorAddress', 'FocusZipcode']:
            return False
        if db in ['sherpa-2', 'sherpa-2.5', 'focus']:
            return False
        return None
