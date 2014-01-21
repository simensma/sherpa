from django.shortcuts import render
from django.core.cache import cache

from datetime import datetime, date
from lxml import etree
import requests
import re

# This ugly import hack imports the model from views because of namespace collision,
# should be 'from aktiviteter.models import Aktivitet'
from aktiviteter.views import Aktivitet
from focus.models import Actor
from page.models import Page
from user.models import User

def index(request):
    total_membership_count = cache.get('admin.total_membership_count')
    local_membership_count = cache.get('admin.local_membership_count.%s' % request.session['active_association'].id)
    if total_membership_count is None or local_membership_count is None:
        all_members = Actor.all_members()
        total_membership_count = all_members.count()
        local_membership_count = all_members.filter(
            main_association_id=request.session['active_association'].get_main_association().focus_id
        ).count()
        cache.set('admin.total_membership_count', total_membership_count, 60 * 60 * 12)
        cache.set('admin.local_membership_count.%s' % request.session['active_association'].id, local_membership_count, 60 * 60 * 12)

    turledere = User.objects.filter(turledere__isnull=False).distinct().count()
    if request.session['active_association'].site is not None:
        pages = Page.on(request.session['active_association'].site).filter(
            pub_date__lte=datetime.now(),
            published=True
        ).count()
    else:
        pages = None
    aktiviteter = Aktivitet.objects.filter(
        pub_date__lte=date.today(),
        published=True,
        private=False,
    ).count()
    dashboard_stats = {
        'members': {
            'total': "{:,}".format(total_membership_count),
            'local': "{:,}".format(local_membership_count),
        },
        'turledere': turledere,
        'pages': pages,
        'aktiviteter': aktiviteter,
    }

    betablog = cache.get('admin.betablog')
    if betablog is None:
        try:
            betablog = []
            r = requests.get("http://beta.turistforeningen.no/", params={'feed': 'rss2'})
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
        except requests.ConnectionError:
            pass

        cache.set('admin.betablog', betablog, 60 * 60 * 12)

    context = {
        'betablog': betablog,
        'dashboard_stats': dashboard_stats,
    }
    return render(request, 'common/admin/dashboard.html', context)

def intro(request):
    return render(request, 'common/admin/intro.html')
