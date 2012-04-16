from page.models import Menu

import re

def menus(request):
    menus = Menu.objects.all().order_by('order')
    for menu in menus:
        if request.get_host() + request.path == re.sub('http:\/\/', '', menu.url):
            menu.active = True
            break
    return {'menus': menus}
