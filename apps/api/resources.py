from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authentication import SessionAuthentication

from aktiviteter.models import Aktivitet, AktivitetDate
from user.models import User
from .authorization import AuthedUserAuthorization

class AktivitetResource(ModelResource):
    class Meta:
        queryset = Aktivitet.objects.all()
        resource_name = 'aktivitet'

class AktivitetDateResource(ModelResource):
    aktivitet = fields.ForeignKey(AktivitetResource, 'aktivitet')

    class Meta:
        queryset = AktivitetDate.objects.all()
        resource_name = 'aktivitet-date'

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['identifier']
        authentication = SessionAuthentication()
        authorization = AuthedUserAuthorization()
        allowed_methods = ['get']

    def dehydrate(self, bundle):
        bundle.data['first_name'] = bundle.obj.get_first_name()
        bundle.data['last_name'] = bundle.obj.get_last_name()
        return bundle
