from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.core.cache import cache

from sherpa2.models import Forening as Sherpa2Forening
from sherpa2.util import COUNTIES_SHERPA2_SET1 as COUNTIES_SHERPA2
from core.models import County

import json

def index(request):
    counties = County.typical_objects().exclude(code='21').order_by('code') # Exclude Svalbard
    # Assign corresponding sherpa-id to the counties, which will be used for filtering
    for county in counties:
        county.sherpa_id = COUNTIES_SHERPA2[county.code]

    for category in Sherpa2Forening.CATEGORIES:
        if request.GET.get('kategori', '') == '' and category['db'] == 'Foreninger':
            category['chosen'] = True
        elif request.GET.get('kategori', '').lower() == category['db'].lower():
            category['chosen'] = True

    full_list = cache.get('foreninger.full_list')
    if full_list is None:
        full_list = Sherpa2Forening.objects.filter(
            Q(type="|Hovedforening") |
            Q(type="|Underforening") |
            Q(type="|Barn") |
            Q(type="|Ungdom") |
            Q(type="|Fjellsport") |
            Q(type="|Senior") |
            Q(type="|Annen")
        ).order_by('name')
        for forening in full_list:
            parent = forening
            while forening.url == '':
                try:
                    parent = Sherpa2Forening.objects.get(id=parent.parent)
                    forening.url = parent.url
                except Sherpa2Forening.DoesNotExist:
                    forening.url = 'ukjent'
        cache.set('foreninger.full_list', full_list, 60 * 60 * 24)

    context = {
        'categories': Sherpa2Forening.CATEGORIES,
        'counties': counties,
        'chosen_county': request.GET.get('fylke', ''),
        'full_list': full_list,
    }
    return render(request, 'main/foreninger/list.html', context)

def visit(request):
    foreninger = Sherpa2Forening.objects.filter(type="|Hovedforening").exclude(visit_address='').order_by('name')
    context = {'foreninger': foreninger}
    return render(request, 'main/foreninger/visit.html', context)

def filter(request):
    if not 'category' in request.POST or not 'county' in request.POST:
        return redirect('foreninger.views.index')
    result = cache.get('foreninger.filter.%s.%s' % (request.POST['category'].title(), request.POST['county']))
    if result is None:
        exists = False
        for category in Sherpa2Forening.CATEGORIES:
            if request.POST['category'].title() == category['db']:
                exists = True
                break
        if not exists:
            # Invalid category provided
            return HttpResponse(json.dumps({}))
        if request.POST['category'].title() == 'Sherpa2Foreninger':
            # Special case, include both of the following:
            foreninger = Sherpa2Forening.objects.filter(Q(type="|Hovedforening") | Q(type="|Underforening"))
        else:
            foreninger = Sherpa2Forening.objects.filter(type="|%s" % request.POST['category'].title())
        if request.POST['county'] != 'all':
            # Sherpa stores foreninger with multiple counties as text with '|' as separator :(
            # So we'll have to pick all of them and programatically check the county
            filter_ids = []
            for forening in foreninger.exclude(county=None):
                if request.POST['county'] in forening.county.split('|'):
                    filter_ids.append(forening.id)
            foreninger = foreninger.filter(id__in=filter_ids)

        foreninger = foreninger.order_by('name')
        result = []

        for forening in foreninger:
            # Assign parents
            parents = []
            try:
                parent = Sherpa2Forening.objects.get(id=forening.parent)
                while parent is not None:
                    parents.append(parent)
                    parent = Sherpa2Forening.objects.get(id=parent.parent)
            except Sherpa2Forening.DoesNotExist:
                pass

            # If the forening has no address, use the parents address
            if forening.post_address == '':
                for parent in parents:
                    if parent.post_address != '':
                        forening.post_address = parent.post_address
                        forening.visit_address = parent.visit_address
                        forening.zipcode = parent.zipcode
                        forening.ziparea = parent.ziparea
                        break

            # Render the forening result
            context = RequestContext(request, {'forening': forening, 'parents': parents})
            result.append(render_to_string('main/foreninger/result.html', context))
        cache.set('foreninger.filter.%s.%s' % (request.POST['category'].title(), request.POST['county']), result, 60 * 60 * 24)
    return HttpResponse(json.dumps(result))
