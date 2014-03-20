from django.http import HttpResponse
from django.core import serializers
from django.shortcuts import render

from core.models import Tag, Zipcode, County, Municipality

import json

def zipcode(request):
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
