from django.core.urlresolvers import resolve
from django.conf import settings
from django.core.cache import cache

from page.models import Menu

import re

def menus(request):
    if request.is_ajax():
        return {}
    else:
        menus = cache.get('main.menu')
        if menus == None:
            menus = Menu.objects.all().order_by('order')
            cache.set('main.menu', menus, 60 * 60 * 24)
        for menu in menus:
            url = re.sub('https?:\/\/', '', menu.url) # Strip protocol
            # Add final slash if missing
            if url[-1] != '/':
                url = "%s/" % url
            if request.get_host() + request.path == url:
                menu.active = True
                break
        return {'menus': menus}

def old_site(request):
    return {'old_site': settings.OLD_SITE}
