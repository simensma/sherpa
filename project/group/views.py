from django.shortcuts import render
from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader
from django.core.cache import cache

from group.models import Group
from user.models import *

import json

# Define categories and their order here. This is duplicated in the Sherpa DB.
categories = [
    {'name': 'Turistforeninger/turlag', 'db': 'Foreninger'},
    {'name': 'Barnas Turlag', 'db': 'Barn'},
    {'name': 'DNT ung', 'db': 'Ungdom'},
    {'name': 'DNT fjellsport', 'db': 'Fjellsport'},
    {'name': 'DNT senior', 'db': 'Senior'},
    {'name': 'Andre turgrupper', 'db': 'Annen'}]

def index(request):
    counties = County.objects.exclude(sherpa_id=None).order_by('code')
    context = {'categories': categories, 'counties': counties,
        'chosen_category': request.GET.get('kategori', ''),
        'chosen_county': request.GET.get('fylke', '')
    }
    return render(request, 'groups/list.html', context)

def filter(request):
    if not request.POST.has_key('category') or not request.POST.has_key('county'):
        return HttpResponseRedirect(reverse('group.views.index'))
    result = cache.get('groups.filter.%s.%s' % (request.POST['category'].title(), request.POST['county']))
    if result == None:
        exists = False
        for category in categories:
            if request.POST['category'].title() == category['db']:
                exists = True
                break
        if not exists:
            # Invalid category provided
            return HttpResponse('{}')
        if request.POST['category'].title() == 'Foreninger':
            # Special case, include both of the following:
            groups = Group.objects.filter(Q(type="|Hovedforening") | Q(type="|Underforening"))
        else:
            groups = Group.objects.filter(type="|%s" % request.POST['category'].title())
        if request.POST['county'] != 'all':
            # Sherpa stores groups with multiple counties as text with '|' as separator :(
            # So we'll have to pick all of them and programatically check the county
            filter_ids = []
            for group in groups.exclude(county=None):
                if request.POST['county'] in group.county.split('|'):
                    filter_ids.append(group.id)
            groups = groups.filter(id__in=filter_ids)

        groups = groups.order_by('name')
        result = []

        for group in groups:
            # Assign parents
            parents = []
            try:
                parent = Group.objects.get(id=group.parent)
                while parent != None:
                    parents.append(parent)
                    parent = Group.objects.get(id=parent.parent)
            except Group.DoesNotExist:
                pass

            # If the group has no address, use the parents address
            if group.post_address == '':
                for parent in parents:
                    if parent.post_address != '':
                        group.post_address = parent.post_address
                        group.visit_address = parent.visit_address
                        group.zip = parent.zip
                        group.ziparea = parent.ziparea
                        break

            # Render the group result
            t = loader.get_template('groups/group-result.html')
            r = RequestContext(request, {'group': group, 'parents': parents})
            result.append(t.render(r))
        cache.set('groups.filter.%s.%s' % (request.POST['category'].title(), request.POST['county']), result, 60 * 60 * 24)
    return HttpResponse(json.dumps(result))
