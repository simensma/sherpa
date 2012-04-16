from page.models import Menu

import re

def menus(request):
    menus = Menu.objects.all().order_by('order')
    for menu in menus:
        url = re.sub('https?:\/\/', '', menu.url) # Strip protocol
        url = re.sub('[^\/]$', '/', url) # Add final slash if missing
        if request.get_host() + request.path == url:
            menu.active = True
            break
    return {'menus': menus}
