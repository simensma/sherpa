from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.db.models import Max
from project.page.models import Menu, Page, PageVariant

def list(request):
    menus = Menu.objects.all().order_by('position')
    for menu in menus:
        menu.page.active = PageVariant.objects.filter(page=menu.page).get(active=True)
    pages = Page.objects.filter(menu__isnull=True)
    for page in pages:
        page.active = PageVariant.objects.filter(page=page).get(active=True)
    context = {'menus': menus, 'pages': pages}
    return render(request, 'admin/cms/menu.html', context)

def new(request):
    page = Page.objects.get(id=request.POST['page'])
    max_order = Menu.objects.aggregate(Max('order'))['order__max']
    if(max_order is None):
        max_order = 0
    menu = Menu(name=request.POST['name'], page=page, order=(max_order + 1))
    menu.save()
    return HttpResponseRedirect(reverse('admin.cms.views.page.list'))

def delete(request, menu):
    menu = Menu.objects.get(id=menu)
    offset = menu.order
    menu.delete()
    # Cascade orders
    menus = Menu.objects.all().filter(order__gt=offset).order_by('order')
    for menu in menus:
        menu.order = offset
        menu.save()
        offset += 1
    return HttpResponseRedirect(reverse('admin.cms.views.page.list'))

def swap(request, order1, order2):
    menu1 = Menu.objects.get(order=order1)
    menu2 = Menu.objects.get(order=order2)
    menu1.order = order2
    menu2.order = order1
    menu1.save()
    menu2.save()
    return HttpResponseRedirect(reverse('admin.cms.views.page.list'))
