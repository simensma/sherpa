from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.db.models import Max
from django.contrib.auth.decorators import login_required
from project.page.models import Menu, Page, Variant

@login_required
def new(request):
    page = Page.objects.get(id=request.POST['page'])
    max_order = Menu.objects.aggregate(Max('order'))['order__max']
    if(max_order is None):
        max_order = 0
    menu = Menu(name=request.POST['name'], page=page, order=(max_order + 1))
    menu.save()
    return HttpResponseRedirect(reverse('admin.cms.views.page.list'))

@login_required
def delete(request, menu):
    Menu.objects.get(id=menu).delete()
    return HttpResponseRedirect(reverse('admin.cms.views.page.list'))

@login_required
def swap(request, order1, order2):
    menu1 = Menu.objects.get(order=order1)
    menu2 = Menu.objects.get(order=order2)
    menu1.order = order2
    menu2.order = order1
    menu1.save()
    menu2.save()
    return HttpResponseRedirect(reverse('admin.cms.views.page.list'))
