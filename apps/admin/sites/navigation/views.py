import json

from django.shortcuts import render
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse

from page.models import Menu
from core.models import Site
from admin.util import url_picker_context

def index(request, site):
    active_site = Site.objects.get(id=site)
    menus = Menu.on(active_site).all().order_by('order')
    context = {
        'active_site': active_site,
        'menus': menus,
    }
    context.update(url_picker_context(active_site))
    return render(request, 'common/admin/sites/navigation/index.html', context)

def save_menu(request, site):
    active_site = Site.objects.get(id=site)
    menus = json.loads(request.POST['menus'])

    # Empty string should be prevented client-side; enforce it here because it would be impossible to edit that item
    if any([m['name'].strip() == '' for m in menus]):
        raise PermissionDenied

    # Delete all existing menus
    Menu.on(active_site).delete()

    # Recreate the new menu set
    for i, menu in enumerate(menus):
        menu = Menu(
            name=menu['name'],
            url=menu['url'],
            order=i,
            site=active_site,
        )
        menu.save()

    # Reset the cache with the new query set
    cache.set('main.menu.%s' % active_site.id, Menu.on(request.site).all().order_by('order'), 60 * 60 * 24)

    # An empty http response will be considered success
    return HttpResponse()
