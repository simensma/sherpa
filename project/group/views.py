from django.shortcuts import render
from django.db.models import Count, Q
from django.http import HttpResponse
from django.template import RequestContext, loader

from group.models import Group
from user.models import *

import json

# Define categories and their order here. This is duplicated in the Sherpa DB.
categories = [
    {'name': 'Medlemsforeninger', 'db': 'Hovedforening'},
    {'name': 'Lokale turlag', 'db': 'Underforening'},
    {'name': 'Barnas turlag', 'db': 'Barn'},
    {'name': 'Ungdomsgrupper', 'db': 'Ungdom'},
    {'name': 'Fjellsportgrupper', 'db': 'Fjellsport'},
    {'name': 'Seniorgrupper', 'db': 'Senior'},
    {'name': 'Andre turgrupper', 'db': 'Annen'}]

def index(request):
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
    groups = Group.objects.all()
    if request.POST['category'] != 'all':
        exists = False
        for category in categories:
            if request.POST['category'].title() == category['db']:
                exists = True
                break
        if not exists:
            # Invalid category provided
            return HttpResponse('{}')
        groups = groups.filter(type="|%s" % request.POST['category'].title())
    if request.POST['county'] != 'all':
        codes = []
        for zip in Zipcode.objects.filter(city_code__startswith=request.POST['county']):
            codes.append(zip.zip_code)
        groups = groups.filter(zip__in=codes)
    result = []
    for g in groups:
        t = loader.get_template('groups/group-result.html')
        r = RequestContext(request, {'group': g})
        result.append(t.render(r))
    return HttpResponse(json.dumps(result))
