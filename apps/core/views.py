from django.http import HttpResponse
from django.core import serializers
from django.shortcuts import render

from core.models import Tag, Zipcode

import json

def zipcode(request, zipcode):
    try:
        # Django serializers can only serialize lists
        zipcode = serializers.serialize("python", [Zipcode.objects.get(zipcode=zipcode)])[0]['fields']
        return HttpResponse(json.dumps(zipcode))
    except Zipcode.DoesNotExist:
        return HttpResponse(json.dumps({'error': 'does_not_exist'}))

def filter_tags(request):
    tag_objects = Tag.objects.filter(name__icontains=request.POST['name'])
    tags = [tag.name for tag in tag_objects]
    return HttpResponse(json.dumps(tags))

def attribution(request):
    return render(request, 'main/attribution.html')
