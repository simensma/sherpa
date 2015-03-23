from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authentication import SessionAuthentication

from aktiviteter.models import Aktivitet, AktivitetDate, ParticipantGroup
from user.models import User
from .authorization import AuthedUserAuthorization, ParticipantAuthorization, ParticipantGroupAuthorization

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
        fields = ['id']
        authentication = SessionAuthentication()
        authorization = AuthedUserAuthorization()
        allowed_methods = ['get']

    def dehydrate(self, bundle):
        # User object status
        bundle.data['is_member'] = bundle.obj.is_member()

        # Personalia
        bundle.data['first_name'] = bundle.obj.get_first_name()
        bundle.data['last_name'] = bundle.obj.get_last_name()
        bundle.data['email'] = bundle.obj.get_email()
        bundle.data['phone_mobile'] = bundle.obj.get_phone_mobile()

        # Data available only for members
        if bundle.obj.is_member():
            bundle.data['memberid'] = bundle.obj.memberid
            bundle.data['gender'] = bundle.obj.get_gender()

            dob = bundle.obj.get_birth_date()
            if dob is not None:
                dob = dob.strftime("%Y-%m-%d")
            bundle.data['dob'] = dob

            address = bundle.obj.get_address()
            bundle.data['address'] = {
                'address1': address.field1,
                'address2': address.field2,
                'address3': address.field3,
                'postcode': address.zipcode.zipcode if address.country.code == 'NO' else None,
                'postarea': address.zipcode.area.title() if address.country.code == 'NO' else None,
                'country': {
                    'code': address.country.code,
                    'name': address.country.name
                },
            }

        return bundle

class ParticipantResource(UserResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'participant'
        fields = ['id']
        authentication = SessionAuthentication()
        authorization = ParticipantAuthorization()
        allowed_methods = ['get']

class AktivitetSignupResource(ModelResource):
    aktivitet_date = fields.ForeignKey(AktivitetDateResource, 'aktivitet_date')
    participants = fields.ManyToManyField(ParticipantResource, 'participants', full=True)

    class Meta:
        queryset = ParticipantGroup.objects.all()
        resource_name = 'aktivitet-signup'
        authentication = SessionAuthentication()
        authorization = ParticipantGroupAuthorization()
        allowed_methods = ['get']
