from django.conf import settings
from django.core.cache import cache

from page.models import Menu

import re

def menus(request):
    if request.is_ajax():
        return {}
    else:
        menus = cache.get('main.menu')
        if menus is None:
            menus = Menu.on(request.site).all().order_by('order')
            cache.set('main.menu', menus, 60 * 60 * 24)
        for menu in menus:
            url = re.sub('https?:\/\/', '', menu.url) # Strip protocol
            # Add final slash if missing
            if url[-1] != '/':
                url = "%s/" % url
            if "%s%s" % (request.site.domain, request.path) == url:
                menu.active = True
                break
        return {'menus': menus}

def current_site(request):
    return {'site': request.site}

def old_site(request):
    return {'old_site': settings.OLD_SITE}

def admin_active_association(request):
    if request.user.is_authenticated() and request.user.has_perm('user.sherpa') and request.path.startswith('/sherpa/'):
        return {'active_association': request.session.get('active_association', '')}
    return {}
