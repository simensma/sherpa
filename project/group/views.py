from django.shortcuts import render
from django.db.models import Count
from django.http import HttpResponse
from django.core import serializers

from group.models import Group
from user.models import *

import json

def index(request):
    categories = Group.objects.exclude(type='').order_by('type').distinct('type')
    counties = County.objects.all().order_by('code')
    context = {'categories': categories, 'counties': counties}
    return render(request, 'groups/list.html', context)

def filter(request):
    group_objs = Group.objects.all()
    if request.POST['category'] != 'all':
        group_objs = group_objs.filter(type=request.POST['category'])
    if request.POST['county'] != 'all':
        codes = []
        for zip in Zipcode.objects.filter(city_code__startswith=request.POST['county']):
            codes.append(zip.zip_code)
        group_objs = group_objs.filter(zip__in=codes)
    groups = []
    for group in group_objs:
        groups.append({'name': group.name})
    return HttpResponse(serializers.serialize('json', group_objs))
