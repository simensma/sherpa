from django.shortcuts import render
from django.db.models import Count, Q
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.core.cache import cache

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
    cached_filter = cache.get('groups.filter.%s.%s' % (request.POST['category'].title(), request.POST['county']))
    if cached_filter != None:
        return HttpResponse(json.dumps(cached_filter))

    exists = False
    for category in categories:
        if request.POST['category'].title() == category['db']:
            exists = True
            break
    if not exists:
        # Invalid category provided
        return HttpResponse('{}')
    groups = Group.objects.filter(type="|%s" % request.POST['category'].title())
    if request.POST['county'] != 'all':
        # Sherpa stores groups with multiple counties as text with '|' as separator :(
        # So we'll have to pick all of them and programatically check the county
        filter_ids = []
        for group in groups.exclude(county=None):
            if request.POST['county'] in group.county.split('|'):
                filter_ids.append(group.id)
        groups = groups.filter(id__in=filter_ids)
    result = []
    for g in groups:
        # If the group has no address, use the parents address
        if g.post_address == '':
            next_parent = g.parent
            while g.post_address == '':
                try:
                    parent = Group.objects.get(id=next_parent)
                    g.post_address = parent.post_address
                    g.visit_address = parent.visit_address
                    g.zip = parent.zip
                    g.ziparea = parent.ziparea
                    next_parent = parent.parent
                except Group.DoesNotExist:
                    break

        # Render the group result
        t = loader.get_template('groups/group-result.html')
        r = RequestContext(request, {'group': g})
        result.append(t.render(r))
    cache.set('groups.filter.%s.%s' % (request.POST['category'].title(), request.POST['county']), result, 60 * 60 * 24)
    return HttpResponse(json.dumps(result))
