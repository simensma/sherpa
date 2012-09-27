from django.shortcuts import render
from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader
from django.core.cache import cache

from association.models import Association
from user.models import *

import json

# Define categories and their order here. This is duplicated in the Sherpa DB.
def get_categories():
    return [
        {'name': 'Turistforeninger/turlag', 'db': 'Foreninger'},
        {'name': 'Barnas Turlag', 'db': 'Barn'},
        {'name': 'DNT ung', 'db': 'Ungdom'},
        {'name': 'DNT fjellsport', 'db': 'Fjellsport'},
        {'name': 'DNT senior', 'db': 'Senior'},
        {'name': 'Andre turgrupper', 'db': 'Annen'}]

def index(request):
    counties = County.objects.exclude(sherpa_id=None).order_by('code')
    categories = get_categories()

    for category in categories:
        if request.GET.get('kategori', '') == '' and category['db'] == 'Foreninger':
            category['chosen'] = True
        elif request.GET.get('kategori', '').lower() == category['db'].lower():
            category['chosen'] = True

    full_list = cache.get('associations.full_list')
    if full_list == None:
        full_list = Association.objects.all().order_by('name')
        for association in full_list:
            parent = association
            while association.url == '':
                try:
                    parent = Association.objects.get(id=parent.parent)
                    association.url = parent.url
                except Association.DoesNotExist:
                    association.url = 'ukjent'
        cache.set('associations.full_list', full_list, 60 * 60 * 24)

    context = {'categories': categories, 'counties': counties,
        'chosen_county': request.GET.get('fylke', ''),
        'full_list': full_list,
    }
    return render(request, 'associations/list.html', context)

def filter(request):
    if not request.POST.has_key('category') or not request.POST.has_key('county'):
        return HttpResponseRedirect(reverse('association.views.index'))
    result = cache.get('associations.filter.%s.%s' % (request.POST['category'].title(), request.POST['county']))
    if result == None:
        exists = False
        for category in get_categories():
            if request.POST['category'].title() == category['db']:
                exists = True
                break
        if not exists:
            # Invalid category provided
            return HttpResponse('{}')
        if request.POST['category'].title() == 'Foreninger':
            # Special case, include both of the following:
            associations = Association.objects.filter(Q(type="|Hovedforening") | Q(type="|Underforening"))
        else:
            associations = Association.objects.filter(type="|%s" % request.POST['category'].title())
        if request.POST['county'] != 'all':
            # Sherpa stores associations with multiple counties as text with '|' as separator :(
            # So we'll have to pick all of them and programatically check the county
            filter_ids = []
            for association in associations.exclude(county=None):
                if request.POST['county'] in association.county.split('|'):
                    filter_ids.append(association.id)
            associations = associations.filter(id__in=filter_ids)

        associations = associations.order_by('name')
        result = []

        for association in associations:
            # Assign parents
            parents = []
            try:
                parent = Association.objects.get(id=association.parent)
                while parent != None:
                    parents.append(parent)
                    parent = Association.objects.get(id=parent.parent)
            except Association.DoesNotExist:
                pass

            # If the association has no address, use the parents address
            if association.post_address == '':
                for parent in parents:
                    if parent.post_address != '':
                        association.post_address = parent.post_address
                        association.visit_address = parent.visit_address
                        association.zip = parent.zip
                        association.ziparea = parent.ziparea
                        break

            # Render the association result
            t = loader.get_template('associations/result.html')
            r = RequestContext(request, {'association': association, 'parents': parents})
            result.append(t.render(r))
        cache.set('associations.filter.%s.%s' % (request.POST['category'].title(), request.POST['county']), result, 60 * 60 * 24)
    return HttpResponse(json.dumps(result))
