from __future__ import absolute_import

from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Max
from page.models import Menu, Page, Variant

import json

def new(request):
    max_order = Menu.objects.aggregate(Max('order'))['order__max']
    if max_order is None:
        max_order = 0
    menu = Menu(name=request.POST['name'], url=request.POST['url'], order=(max_order + 1))
    menu.save()
    return HttpResponse(json.dumps({'id': menu.id}))

def edit(request, menu):
    menu = Menu.objects.get(id=menu)
    menu.name = request.POST['name']
    menu.url = request.POST['url']
    menu.save()
    return HttpResponse()

def delete(request, menu):
    Menu.objects.get(id=menu).delete()
    return HttpResponseRedirect(reverse('admin.cms.views.page.list'))

def reorder(request):
    for menu in json.loads(request.POST['menus']):
        obj = Menu.objects.get(id=menu['id'])
        obj.order = menu['order']
        obj.save()
    return HttpResponse()
