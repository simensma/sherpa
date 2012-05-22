class Router(object):
    def db_for_read(self, model, **hints):
        if model._meta.object_name == 'Group':
            return 'sherpa-2'
        elif model._meta.object_name == 'FocusUser' or model._meta.object_name == 'FocusActType' or model._meta.object_name == 'Actor' or model._meta.object_name == 'ActorAddress':
            return 'focus'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.object_name == 'Group' or model._meta.object_name == 'Actor' or model._meta.object_name == 'ActorAddress':
            raise Exception("Don't write to this model!")
        elif model._meta.object_name == 'FocusUser' or model._meta.object_name == 'FocusActType':
            return 'focus'
        return None

    def allow_syncdb(self, db, model):
        if model._meta.object_name == 'Group':
            return False
        if model._meta.object_name == 'FocusUser' or model._meta.object_name == 'FocusActType' or model._meta.object_name == 'Actor' or model._meta.object_name == 'ActorAddress':
            return False
        if db in ['sherpa-2', 'sherpa-2.5', 'focus']:
            return False
        return None
