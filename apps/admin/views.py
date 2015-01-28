from datetime import datetime, date
import re

from django.shortcuts import render
from django.core.cache import cache
from django.db.models import Q

from lxml import etree
import requests

# This ugly import hack imports the model from views because of namespace collision,
# should be 'from aktiviteter.models import Aktivitet'
from aktiviteter.views import Aktivitet
from focus.models import Actor
from user.models import User

def index(request):
    total_membership_count = cache.get('admin.total_membership_count')
    local_membership_count = cache.get('admin.local_membership_count.%s' % request.active_forening.id)
    if total_membership_count is None or local_membership_count is None:
        if request.db_connections['focus']['is_available']:
            all_active_members = Actor.all_active_members()
            total_membership_count = all_active_members.count()
            local_membership_count = all_active_members.filter(
                main_forening_id__in=[f.focus_id for f in request.active_forening.get_main_foreninger()],
            ).count()
            cache.set('admin.total_membership_count', total_membership_count, 60 * 60 * 12)
            cache.set('admin.local_membership_count.%s' % request.active_forening.id, local_membership_count, 60 * 60 * 12)
        else:
            # Fallback if Focus is down
            total_membership_count = None
            local_membership_count = None

    turledere = cache.get('admin.turleder_count')
    if turledere is None:
        turledere = User.get_users().filter(turledere__isnull=False).distinct().count()
        cache.set('admin.turleder_count', turledere, 60 * 60 * 6)

    aktiviteter = cache.get('admin.aktivitet_count')
    if aktiviteter is None:
        aktiviteter = Aktivitet.objects.filter(
            Q(forening=request.active_forening) |
            Q(co_foreninger=request.active_forening),
            pub_date__lte=date.today(),
            published=True,
            private=False,
        ).count()
        cache.set('admin.aktivitet_count', aktiviteter, 60 * 60 * 6)

    dashboard_stats = {
        'members': {
            'total': "{:,}".format(total_membership_count) if total_membership_count is not None else '?',
            'local': "{:,}".format(local_membership_count) if local_membership_count is not None else '?',
        },
        'turledere': turledere,
        'aktiviteter': aktiviteter,
    }

    betablog = cache.get('admin.betablog')
    if betablog is None:
        try:
            betablog = []
            r = requests.get("http://beta.dnt.no/", params={'feed': 'rss2'})
            channel = etree.fromstring(r.content).find('channel')
            for item in channel.findall('item'):
                content = item.find('description').text
                image = None
                m = re.search('<img.*?src="(.*?)" ', content)
                if m is not None:
                    image = m.group(1)
                pub_date = datetime.strptime(item.find('pubDate').text[:-6], "%a, %d %b %Y %H:%M:%S")

                betablog.append({
                    'title': item.find('title').text,
                    'link': item.find('link').text,
                    'content': content,
                    'image': image,
                    'pub_date': pub_date,
                })
        except (requests.ConnectionError, AttributeError):
            pass

        cache.set('admin.betablog', betablog, 60 * 60 * 12)

    context = {
        'betablog': betablog,
        'dashboard_stats': dashboard_stats,
    }
    return render(request, 'common/admin/dashboard.html', context)
