from django.shortcuts import render, redirect
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.db.models import Max

from page.models import Menu
from core.models import Site

import json

def index(request, site):
    active_site = Site.objects.get(id=site)
    menus = Menu.on(active_site).all().order_by('order')
    context = {
        'active_site': active_site,
        'menus': menus,
    }
    return render(request, 'common/admin/sites/navigation/index.html', context)

def new_menu(request, site):
    active_site = Site.objects.get(id=site)
    if request.POST['name'].strip() == '':
        raise PermissionDenied

    max_order = Menu.on(active_site).aggregate(Max('order'))['order__max']
    if max_order is None:
        max_order = 0
    menu = Menu(
        name=request.POST['name'],
        url=request.POST['url'],
        order=(max_order + 1),
        site=active_site
    )
    menu.save()
    cache.delete('main.menu.%s' % active_site.id)
    return HttpResponse(json.dumps({'id': menu.id}))

def edit_menu(request, site):
    active_site = Site.objects.get(id=site)
    if request.POST['name'].strip() == '':
        raise PermissionDenied

    menu = Menu.on(active_site).get(id=request.POST['id'])
    menu.name = request.POST['name']
    menu.url = request.POST['url']
    menu.save()
    cache.delete('main.menu.%s' % active_site.id)
    return HttpResponse()

def delete_menu(request, site):
    active_site = Site.objects.get(id=site)
    Menu.on(active_site).get(id=request.POST['menu']).delete()
    cache.delete('main.menu.%s' % active_site.id)
    return redirect('admin.sites.sites.navigation.views.index')

def reorder_menu(request, site):
    active_site = Site.objects.get(id=site)
    for menu in json.loads(request.POST['menus']):
        obj = Menu.on(active_site).get(id=menu['id'])
        obj.order = menu['order']
        obj.save()
    cache.delete('main.menu.%s' % active_site.id)
    return HttpResponse()
