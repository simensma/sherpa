from __future__ import absolute_import

from django.shortcuts import redirect
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.db.models import Max
from page.models import Menu

import json

def new(request):
    if request.POST['name'].strip() == '':
        raise PermissionDenied

    max_order = Menu.on(request.session['active_forening'].site).aggregate(Max('order'))['order__max']
    if max_order is None:
        max_order = 0
    menu = Menu(name=request.POST['name'], url=request.POST['url'], order=(max_order + 1), site=request.session['active_forening'].site)
    menu.save()
    cache.delete('main.menu')
    return HttpResponse(json.dumps({'id': menu.id}))

def edit(request):
    if request.POST['name'].strip() == '':
        raise PermissionDenied

    menu = Menu.on(request.session['active_forening'].site).get(id=request.POST['id'])
    menu.name = request.POST['name']
    menu.url = request.POST['url']
    menu.save()
    cache.delete('main.menu')
    return HttpResponse()

def delete(request):
    Menu.on(request.session['active_forening'].site).get(id=request.POST['menu']).delete()
    cache.delete('main.menu')
    return redirect('admin.cms.views.page.list')

def reorder(request):
    for menu in json.loads(request.POST['menus']):
        obj = Menu.on(request.session['active_forening'].site).get(id=menu['id'])
        obj.order = menu['order']
        obj.save()
    cache.delete('main.menu')
    return HttpResponse()
