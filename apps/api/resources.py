from tastypie.resources import ModelResource
from aktiviteter.models import Aktivitet

class AktivitetResource(ModelResource):
    class Meta:
        queryset = Aktivitet.objects.all()
        resource_name = 'aktivitet'
