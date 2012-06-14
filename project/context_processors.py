from django.core.urlresolvers import resolve
from django.conf import settings

from page.models import Menu

import re

def menus(request):
    if request.is_ajax():
        return {}
    else:
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

def old_site(request):
    return {'old_site': settings.OLD_SITE}

def first_visit(request):
    context = {}
    if not request.session.has_key('first_visit'):
        request.session['first_visit'] = True
        context['first_visit'] = True
    return context
