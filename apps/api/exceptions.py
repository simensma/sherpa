# We'd like to use BadRequest like Django's PermissionDenied exception here
class BadRequest(Exception):
    pass
