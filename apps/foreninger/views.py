from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.core.cache import cache
from django.core.exceptions import PermissionDenied

from foreninger.models import Forening
from core.models import County

import json

def index(request):
    counties = County.typical_objects().exclude(code='21').order_by('code') # Exclude Svalbard

    full_list = cache.get('foreninger.full_list')
    if full_list is None:
        full_list = [
            (f.name, f.get_site_or_old_url() or f.get_main_forenings()[0].get_site_or_old_url())
            for f in Forening.objects.order_by('name')
        ]
        cache.set('foreninger.full_list', full_list, 60 * 60 * 24 * 7)

    context = {
        'categories': Forening.PUBLIC_CATEGORIES,
        'chosen_category': request.GET.get('kategori', 'foreninger').lower(),
        'counties': counties,
        'chosen_county': request.GET.get('fylke', ''),
        'full_list': full_list,
    }
    return render(request, 'main/foreninger/list.html', context)

def visit(request):
    foreninger = Forening.objects.filter(type='forening').exclude(visit_address='').order_by('name')
    context = {'foreninger': foreninger}
    return render(request, 'main/foreninger/visit.html', context)

def filter(request):
    if not 'category' in request.POST or not 'county' in request.POST:
        return redirect('foreninger.views.index')

    result = cache.get('foreninger.filter.%s.%s' % (request.POST['category'], request.POST['county']))
    if result is None:
        if request.POST['category'] not in [c[0] for c in Forening.PUBLIC_CATEGORIES]:
            # Invalid category provided
            raise PermissionDenied

        foreninger = Forening.objects.all()
        if request.POST['category'] == 'foreninger':
            # Special case, include both of the following:
            foreninger = foreninger.filter(Q(type='forening') | Q(type='turlag'))
        else:
            foreninger = foreninger.filter(type='turgruppe', group_type=request.POST['category'])

        if request.POST['county'] != 'all':
            foreninger = foreninger.filter(counties=request.POST['county'])

        foreninger = foreninger.order_by('name')

        result = [render_to_string('main/foreninger/result.html', RequestContext(request, {
            'forening': forening,
        })) for forening in foreninger]

        cache.set('foreninger.filter.%s.%s' % (request.POST['category'], request.POST['county']), result, 60 * 60 * 24)

    return HttpResponse(json.dumps(result))
