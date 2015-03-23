from tastypie.authorization import Authorization

class AuthedUserAuthorization(Authorization):
    """A custom tastypie authorization to return only objects for the logged in user. Loosely based on
    https://django-tastypie.readthedocs.org/en/v0.9.12/authorization.html#implementing-your-own-authorization"""
    def read_list(self, object_list, bundle):
        return object_list.filter(pk=bundle.request.user.pk)

    def read_detail(self, object_list, bundle):
        return bundle.obj == bundle.request.user

class ParticipantGroupAuthorization(Authorization):
    """A custom tastypie authorization which gives access to ParticipantGroup objects the user is currently a
    participant in"""
    def read_list(self, object_list, bundle):
        return object_list.filter(participants=bundle.request.user)

    def read_detail(self, object_list, bundle):
        return bundle.obj.participants.filter(pk=bundle.request.user.pk).exists()
