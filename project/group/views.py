from django.shortcuts import render
from django.db.models import Count, Q
from django.http import HttpResponse
from django.core import serializers

from group.models import Group
from user.models import *

import json

def index(request):
    categories = Group.objects.exclude(type='').filter(
        Q(type='|Hovedforening') |
        Q(type='|Underforening') |
        Q(type='|Barn') |
        Q(type='|Ungdom') |
        Q(type='|Fjellsport') |
        Q(type='|Senior') |
        Q(type='|Annet')
        ).order_by('type').distinct('type')
    counties = County.objects.exclude(sherpa_id=None).order_by('code')
    context = {'categories': categories, 'counties': counties,
        'chosen_category': request.GET.get('kategori', ''),
        'chosen_county': request.GET.get('fylke', '')
    }
    return render(request, 'groups/list.html', context)

def filter(request):
    if request.POST['category'] == 'all' and request.POST['county'] == 'all':
        # Shouldn't happen unless someone manually sends such a request
        return HttpResponse('{}')
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
