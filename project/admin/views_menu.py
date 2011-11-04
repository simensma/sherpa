from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.db.models import Max
from page.models import Menu, Page, PageVersion

def menu_list(request, error=None):
    menus = Menu.objects.all().order_by('position')
    for menu in menus:
        menu.page.active = PageVersion.objects.filter(page=menu.page).get(active=True)
    pages = Page.objects.filter(menu__isnull=True)
    for page in pages:
        page.active = PageVersion.objects.filter(page=page).get(active=True)
    context = {'menus': menus, 'pages': pages, 'error': error}
    return render(request, 'admin/menu.html', context)

def menu_add(request, page):
    page = Page.objects.get(pk=page)
    max_position = Menu.objects.aggregate(Max('position'))['position__max']
    if(max_position is None):
        max_position = 0
    menu = Menu(name=request.POST['name'], page=page, position=(max_position + 1))
    menu.save()
    return HttpResponseRedirect(reverse('admin.views.menu_list'))

def menu_remove(request, page):
    menu = Menu.objects.get(page=page)
    offset = menu.position
    menu.delete()
    # Cascade positions
    menus = Menu.objects.all().filter(position__gt=offset).order_by('position')
    for menu in menus:
        menu.position = offset
        menu.save()
        offset += 1
    return HttpResponseRedirect(reverse('admin.views.menu_list'))

def menu_swap(request, pos1, pos2):
    menu1 = Menu.objects.get(position=pos1)
    menu2 = Menu.objects.get(position=pos2)
    menu1.position = pos2
    menu2.position = pos1
    menu1.save()
    menu2.save()
    return HttpResponseRedirect(reverse('admin.views.menu_list'))
