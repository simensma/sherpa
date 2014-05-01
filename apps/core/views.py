from django.http import HttpResponse
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.conf import settings

from core.models import Tag, Zipcode, County, Municipality

from datetime import datetime
import json
import requests

def zipcode(request):
    if not request.is_ajax() or not 'zipcode' in request.POST:
        raise PermissionDenied

    try:
        # Django serializers can only serialize lists
        zipcode = serializers.serialize("python", [Zipcode.objects.get(zipcode=request.POST['zipcode'])])[0]['fields']
        return HttpResponse(json.dumps(zipcode))
    except Zipcode.DoesNotExist:
        return HttpResponse(json.dumps({'error': 'does_not_exist'}))

def filter_tags(request):
    tag_objects = Tag.objects.filter(name__icontains=request.GET['q'].strip())
    tags = [tag.name for tag in tag_objects]
    return HttpResponse(json.dumps(tags))

def attribution(request):
    return render(request, 'main/attribution.html')

def county_lookup(request):
    point_wkt = 'POINT(%s %s)' % (json.loads(request.POST['lng']), json.loads(request.POST['lat']))
    return HttpResponse(json.dumps([c.id for c in County.objects.filter(geom__contains=point_wkt)]))

def municipality_lookup(request):
    point_wkt = 'POINT(%s %s)' % (json.loads(request.POST['lng']), json.loads(request.POST['lat']))
    return HttpResponse(json.dumps([m.id for m in Municipality.objects.filter(geom__contains=point_wkt)]))

def doge(request):
    return render(request, 'main/doge.html')

def booking_spots(request, code, date):
    """This view is used by gamle Sherpa to display available spots in a small iframe next to the signup buttons."""
    date = datetime.strptime(date, "%Y-%m-%d")
    r = requests.get(
        "%s/%s/" % (settings.DNTOSLO_MONTIS_API_URL, code),
        params={
            'client': 'dnt',
            'autentisering': settings.DNTOSLO_MONTIS_API_KEY,
        },
    )
    for tour_date in json.loads(r.text):
        if date == datetime.fromtimestamp(tour_date['startdato']):
            context = {
                'available': tour_date['plasserLedig'],
                'total': tour_date['plasserTotalt'],
                'waiting_list': tour_date['venteliste'],
            }
            return render(request, 'main/booking_spots.html', context)

    # Invalid date? Ignore for now
    return HttpResponse('')
