from tastypie.authorization import Authorization
from tastypie.exceptions import Unauthorized

class AuthedUserAuthorization(Authorization):
    """A custom tastypie authorization to return only objects for the logged in user. Loosely based on
    https://django-tastypie.readthedocs.org/en/v0.9.12/authorization.html#implementing-your-own-authorization"""
    def read_list(self, object_list, bundle):
        return object_list.filter(pk=bundle.request.user.pk)

    def read_detail(self, object_list, bundle):
        return bundle.obj == bundle.request.user

class ParticipantAuthorization(Authorization):
    """A participant can access all other participants in their own group"""
    def read_list(self, object_list, bundle):
        return object_list.filter(aktivitet_groups__participants=bundle.request.user)

    def read_detail(self, object_list, bundle):
        return bundle.obj.aktivitet_groups.select_related().filter(participants=bundle.request.user).exists()

    def create_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no creates.")

    def create_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no creates.")

    def update_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no updates.")

    def update_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no updates.")

    def delete_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")

    def delete_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")

class ParticipantGroupAuthorization(Authorization):
    """A custom tastypie authorization which gives access to ParticipantGroup objects the user is currently a
    participant in"""
    def read_list(self, object_list, bundle):
        return object_list.filter(participants=bundle.request.user)

    def read_detail(self, object_list, bundle):
        return bundle.obj.participants.filter(pk=bundle.request.user.pk).exists()

    def create_list(self, object_list, bundle):
        return object_list

    def create_detail(self, object_list, bundle):
        return True

    def update_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no updates.")

    def update_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no updates.")

    def delete_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")

    def delete_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")
