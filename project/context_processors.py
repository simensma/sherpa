from django.core.urlresolvers import resolve

from page.models import Menu

import re

def menus(request):
    if not request.is_ajax():
        menus = Menu.objects.all().order_by('order')
        for menu in menus:
            url = re.sub('https?:\/\/', '', menu.url) # Strip protocol
            # Add final slash if missing
            if url[-1] != '/':
                url = "%s/" % url
            if request.get_host() + request.path == url:
                menu.active = True
                break
        return {'menus': menus}
