from django.shortcuts import render, redirect
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.db.models import Max

from page.models import Menu

import json

def index(request):
    menus = Menu.on(request.active_forening.get_homepage_site()).all().order_by('order')
    context = {'menus': menus}
    return render(request, 'common/admin/sites/menu/index.html', context)

def new(request):
    if request.POST['name'].strip() == '':
        raise PermissionDenied

    max_order = Menu.on(request.active_forening.get_homepage_site()).aggregate(Max('order'))['order__max']
    if max_order is None:
        max_order = 0
    menu = Menu(name=request.POST['name'], url=request.POST['url'], order=(max_order + 1), site=request.active_forening.get_homepage_site())
    menu.save()
    cache.delete('main.menu.%s' % request.active_forening.get_homepage_site().id)
    return HttpResponse(json.dumps({'id': menu.id}))

def edit(request):
    if request.POST['name'].strip() == '':
        raise PermissionDenied

    menu = Menu.on(request.active_forening.get_homepage_site()).get(id=request.POST['id'])
    menu.name = request.POST['name']
    menu.url = request.POST['url']
    menu.save()
    cache.delete('main.menu.%s' % request.active_forening.get_homepage_site().id)
    return HttpResponse()

def delete(request):
    Menu.on(request.active_forening.get_homepage_site()).get(id=request.POST['menu']).delete()
    cache.delete('main.menu.%s' % request.active_forening.get_homepage_site().id)
    return redirect('admin.sites.sites.menu.views.index')

def reorder(request):
    for menu in json.loads(request.POST['menus']):
        obj = Menu.on(request.active_forening.get_homepage_site()).get(id=menu['id'])
        obj.order = menu['order']
        obj.save()
    cache.delete('main.menu.%s' % request.active_forening.get_homepage_site().id)
    return HttpResponse()
