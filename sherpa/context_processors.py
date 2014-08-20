from datetime import datetime, date

from django.conf import settings
from django.core.cache import cache

from page.models import Menu
from core.models import Site
from core.util import membership_year_start as membership_year_start_date_set, s3_bucket as get_s3_bucket

def menus(request):
    if request.is_ajax():
        return {}
    else:
        menus = cache.get('main.menu.%s' % request.site.id)
        if menus is None:
            menus = Menu.on(request.site).all().order_by('order')
            cache.set('main.menu.%s' % request.site.id, menus, 60 * 60 * 24)
        return {'menus': menus}

def main_site(request):
    return {'main_site': Site.objects.get(id=Site.DNT_CENTRAL_ID)}

def current_site(request):
    return {'site': request.site}

def old_site(request):
    return {'old_site': settings.OLD_SITE}

def admin_active_forening(request):
    if request.user.is_authenticated() and \
       request.user.has_perm('sherpa') and \
       request.path.startswith('/sherpa/') and \
       hasattr(request, 'active_forening'):
        return {'active_forening': request.active_forening}
    return {}

def db_connections(request):
    return {'db_connections': request.db_connections}

def dntconnect(request):
    if 'dntconnect' in request.session:
        client = settings.DNT_CONNECT[request.session['dntconnect']['client_id']]
        return {'dntconnect': {
            'client_id': request.session['dntconnect']['client_id'],
            'client_name': client['friendly_name'],
        }}
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

def current_time(request):
    return {
        'now': datetime.now(),
        'today': date.today(),
    }

def analytics_ua(request):
    """Override the analytics ua with the test-profile if settings.DEBUG is True"""
    if not settings.DEBUG:
        ua = request.site.analytics_ua
    else:
        ua = settings.DEBUG_ANALYTICS_UA
    return {'analytics_ua': ua}

def s3_bucket(request):
    return {'s3_bucket': get_s3_bucket()}
