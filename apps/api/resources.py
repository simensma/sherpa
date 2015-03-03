from tastypie import fields
from tastypie.resources import ModelResource

from aktiviteter.models import Aktivitet, AktivitetDate

class AktivitetResource(ModelResource):
    class Meta:
        queryset = Aktivitet.objects.all()
        resource_name = 'aktivitet'

class AktivitetDateResource(ModelResource):
    aktivitet = fields.ForeignKey(AktivitetResource, 'aktivitet')

    class Meta:
        queryset = AktivitetDate.objects.all()
        resource_name = 'aktivitet-date'
