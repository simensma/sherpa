from django.core.urlresolvers import resolve
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q

from page.models import Menu
from association.models import Association

import re

def menus(request):
    if request.is_ajax():
        return {}
    else:
        menus = cache.get('main.menu')
        if menus is None:
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

def current_site(request):
    return {'site': request.site}

def old_site(request):
    return {'old_site': settings.OLD_SITE}

def admin_user_associations(request):
    if request.path.startswith('/sherpa'):
        user_associations = request.user.get_profile().associations.all().order_by('name')
        association_collection = {
            'central': user_associations.filter(type='sentral'),
            'associations': user_associations.filter(type='forening'),
            'small_associations': user_associations.filter(type='turlag'),
            'hike_groups': user_associations.filter(type='turgruppe'),
        }
        return {'user_associations': association_collection}
    return {}
