from django.conf import settings
from django.core.cache import cache

from page.models import Menu
from core.util import membership_year_start as membership_year_start_date_set

from datetime import datetime, date
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
    if request.user.is_authenticated() and request.user.has_perm('sherpa') and request.path.startswith('/sherpa/'):
        return {'active_association': request.session.get('active_association', '')}
    return {}

def focus_downtime(request):
    now = datetime.now()
    for downtime in settings.FOCUS_DOWNTIME_PERIODS:
        if now >= downtime['from'] and now < downtime['to']:
            return {
                'focus_downtime': {
                    'is_currently_down': True,
                    'period_message': downtime['period_message']
                }
            }
    return {'focus_downtime': {'is_currently_down': False}}

def dntconnect(request):
    if 'dntconnect' in request.session:
        # Note that this sends the shared_secrets to all templates, maybe that isn't such a good idea
        return {'dntconnect': request.session['dntconnect']}
    else:
        return {}

def membership_year_start(request):
    today = date.today()
    date_set = {}
    for key, value in membership_year_start_date_set().items():
        date_set[key] = {
            'date': value,
            'has_passed': today >= value,
            'applicable_year': value.year + 1 if today >= value else today.year
        }
    return {'membership_year_start': date_set}

def do_not_track(request):
    return {'donottrack': 'HTTP_DNT' in request.META and request.META['HTTP_DNT'] == '1'}

def new_sponsors_footer(request):
    """
    Remove this method after 01.01.2014
    """
    return {'new_sponsors': date.today() >= date(year=2014, month=1, day=1)}