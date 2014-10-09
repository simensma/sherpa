import json

from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.core.cache import cache
from django.core.exceptions import PermissionDenied

from foreninger.models import Forening
from core.models import County

def index(request):
    county_objects = County.typical_objects().exclude(code='21').order_by('code') # Exclude Svalbard

    # We'll use a "fake" county to represent the entire country, with a sentinel ID value
    fake_national_county = County(
        id='all',
        name='Hele landet',
    )

    # Prepend "entire country" to the county listing
    counties = [fake_national_county]
    counties.extend(county_objects)

    # Split the counties into groups pre-divided for 3 columns
    counties_three_columns = (
        [county for i, county in enumerate(counties) if i % 3 == 0],
        [county for i, county in enumerate(counties) if (i-1) % 3 == 0],
        [county for i, county in enumerate(counties) if (i-2) % 3 == 0],
    )

    full_list = cache.get('foreninger.all.sorted_by_name.with_active_url')
    if full_list is None:
        all_foreninger_by_name = cache.get('foreninger.all.sorted_by_name')
        if all_foreninger_by_name is None:
            all_foreninger_by_name = list(Forening.objects.order_by('name'))
            cache.set('foreninger.all.sorted_by_name', all_foreninger_by_name, 60 * 60 * 24 * 7)

        full_list = [
            (f.name, f.get_active_url() or f.get_main_foreninger()[0].get_active_url())
            for f in all_foreninger_by_name
        ]
        cache.set('foreninger.all.sorted_by_name.with_active_url', full_list, 60 * 60 * 24 * 7)

    context = {
        'categories': Forening.PUBLIC_CATEGORIES,
        'chosen_category': request.GET.get('kategori', 'foreninger').lower(),
        'counties': counties,
        'counties_three_columns': counties_three_columns,
        'chosen_county_name': request.GET.get('fylke', fake_national_county.name),
        'full_list': full_list,
    }
    return render(request, 'central/foreninger/list.html', context)

def visit(request):
    foreninger = Forening.objects.filter(type='forening').exclude(visit_address='').order_by('name')
    context = {'foreninger': foreninger}
    return render(request, 'central/foreninger/visit.html', context)

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

        result = [render_to_string('central/foreninger/result.html', RequestContext(request, {
            'forening': forening,
        })) for forening in foreninger]

        cache.set('foreninger.filter.%s.%s' % (request.POST['category'], request.POST['county']), result, 60 * 60 * 24)

    return HttpResponse(json.dumps(result))
