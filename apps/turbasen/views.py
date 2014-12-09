# encoding: utf-8
import json

from django.http import HttpResponse

from sherpa2.models import Location, NtbId

def location_lookup(request):
    """Lookup område by point. Currently implemented with sherpa2 locations, and using the NtbId table to map any
    hits to their corresponding object ids.
    TODO use turbase geojson-lookup when ready"""
    point_wkt = 'POINT(%s %s)' % (json.loads(request.POST['lng']), json.loads(request.POST['lat']))
    return HttpResponse(json.dumps([
        NtbId.objects.get(sql_id=location.id, type='L').object_id
        for location in Location.get_active().filter(geom__contains=point_wkt)
    ]))
