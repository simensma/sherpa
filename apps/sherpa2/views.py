import json

from django.http import HttpResponse

from sherpa2.models import Location

def location_lookup(request):
    point_wkt = 'POINT(%s %s)' % (json.loads(request.POST['lng']), json.loads(request.POST['lat']))
    return HttpResponse(json.dumps([m.id for m in Location.get_active().filter(geom__contains=point_wkt)]))
