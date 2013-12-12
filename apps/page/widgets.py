# encoding: utf-8
from django.core.cache import cache
from django.conf import settings

from lxml import etree
from datetime import datetime, date
import requests
import json
import re
import random

from page.models import Version

# Note: This is also imported by some views in admin, and a view in articles
def parse_widget(request, widget):
    if widget['widget'] == "quote":
        data = {'quote': widget['quote'], 'author': widget['author']}
    elif widget['widget'] == 'carousel':
        # NO! BAD HAVARD, dont use hax, create an id(but not now)
        data = {'id':random.randint(0,10000), 'images':widget['images']}
    elif widget['widget'] == "articles":
        versions = Version.objects.filter(
            variant__article__isnull=False,
            variant__segment__isnull=True,
            variant__article__published=True,
            active=True,
            variant__article__pub_date__lt=datetime.now(),
            variant__article__site=request.site
            ).order_by('-variant__article__pub_date')

        for tag in widget['tags']:
            versions = versions.filter(tags__name__icontains=tag).distinct()

        versions = versions[:widget['count']]
        for version in versions:
            version.load_preview()
        data = {
            'title': widget['title'],
            'display_images': widget['display_images'],
            'tag_link': widget['tag_link'],
            'versions': versions
        }
    elif widget['widget'] == "blog":
        # This is a pretty heavy query, so cache it for a while
        data = cache.get('widgets.blog.category.' + widget['category'])
        if data is None:

            feed_url = "http://%s/" % settings.BLOG_URL;

            if widget['category'] != 'Alle':
                feed_url += 'tema/' + widget['category'].lower() + '/'
            feed_url += 'feed/'

            try:
                r = requests.get(feed_url)
                channel = etree.fromstring(r.content).find('channel')
            except requests.ConnectionError:
                channel = None

            entries = []
            entries_matched = 0;
            if channel is not None:
                for item in channel.findall('item'):

                    item_categories = []
                    for item_category in item.findall('category'):
                        item_categories.append(item_category.text)

                    if (widget['category'] in item_categories or widget['category'] == 'Alle'):
                        entries_matched += 1;

                        content = item.find('{http://purl.org/rss/1.0/modules/content/}encoded').text
                        image = None
                        m = re.search('<img.*?src="(.*?)" ', content)
                        if m is not None:
                            image = m.group(1)
                        entries.append({
                            'title': item.find('title').text,
                            'link': item.find('link').text,
                            'content': content,
                            'image': image})
                    if entries_matched >= int(widget['count']):
                        break
            data = {'entries':entries}
            cache.set('widgets.blog.category.' + widget['category'], data, 60 * 30)
    elif widget['widget'] == "embed":
        data = {'code': widget['code']}
    elif widget['widget'] == "fact":
        data = {'content': widget['content']}

    data.update({
        'json': json.dumps(widget),
        'template': 'common/widgets/%s/display.html' % widget['widget'],
        'widget': widget['widget']})
    return data


def widget_admin_context():
    def blog_category_list():
        # The list of categories available in the blogwidget
        categories = cache.get('widgets.blog.category_list')
        if categories is None:
            r = requests.get("http://%s/%s" % (settings.BLOG_URL, settings.BLOG_CATEGORY_API))
            response = json.loads(r.text)
            categories = ['Alle']
            for category in response['categories']:
                if category['id'] == 1:
                    # Uncategorized
                    continue
                categories.append(category['title'])
            cache.set('widgets.blog.category_list', categories, 60 * 60 * 24 * 7)
        return categories

    return {
        'blog': {'categories': blog_category_list()}
    }

# Used temporary for static promo content
def get_static_promo_context(path):

    ROTATIONS = [
        {
            'id': 'final-vennetur',
            'name': '#vennetur',
            'start_date': date(year=2013, month=7, day=4),
            'end_date': date(year=2013, month=7, day=4),
        },
        {
            'id': '10-turer-pa-topp',
            'name': 'Klassikere',
            'start_date': date(year=2013, month=7, day=5),
            'end_date': date(year=2013, month=7, day=14),
        },
        {
            'id': 'bli-medlem',
            'name': 'Medlemskap',
            'start_date': date(year=2013, month=7, day=15),
            'end_date': date(year=2013, month=7, day=21),
        },
        {
            'id': 'hyttetur',
            'name': 'Hyttetur',
            'start_date': date(year=2013, month=7, day=22),
            'end_date': date(year=2013, month=7, day=28),
        },
        {
            'id': '10-turer-pa-topp',
            'name': 'Klassikere',
            'start_date': date(year=2013, month=7, day=29),
            'end_date': date(year=2013, month=8, day=11),
        },
        {
            'id': 'kom-deg-ut',
            'name': 'Kom deg ut',
            'start_date': date(year=2013, month=8, day=12),
            'end_date': date(year=2013, month=9, day=1),
        },
        {
            'id': 'fjellfilm',
            'name': 'Fjellfilm',
            'start_date': date(year=2013, month=9, day=2),
            'end_date': date(year=2013, month=9, day=14),
        },
        {
            'id': 'bli-medlem',
            'name': 'Medlemskap',
            'start_date': date(year=2013, month=9, day=15),
            'end_date': date(year=2013, month=9, day=15),
        },
        {
            'id': 'host',
            'name': 'Høst',
            'start_date': date(year=2013, month=9, day=16),
            'end_date': date(year=2013, month=10, day=10),
        },
        {
            'id': 'fotokonkurranse',
            'name': 'Fotokonkurranse',
            'start_date': date(year=2013, month=10, day=11),
            'end_date': date(year=2013, month=11, day=6),
        },
        {
            'id': 'gjensidige',
            'name': 'Medlemsfordeler',
            'start_date': date(year=2013, month=11, day=7),
            'end_date': date(year=2013, month=11, day=25),
        },
        {
            'id': 'stillenatur',
            'name': '#stillenatur',
            'start_date': date(year=2013, month=11, day=26),
            'end_date': date(year=2013, month=12, day=10),
        },
        {
            'id': 'gavemedlemskap',
            'name': 'Gavemedlemskap',
            'start_date': date(year=2013, month=12, day=11),
            'end_date': date(year=2013, month=12, day=11),
        }
    ]

    today = date.today()
    rotation_hits = [r for r in ROTATIONS if r['start_date'] <= today and r['end_date'] >= today]
    if len(rotation_hits) == 0:
        # No direct hits, pick the latest one from the past
        rotations_from_the_past = [r for r in ROTATIONS if r['end_date'] < today]
        rotation = max(rotations_from_the_past, key=lambda r: r['end_date'])
    elif len(rotation_hits) == 1:
        rotation = rotation_hits[0]
    else:
        raise Exception("There shouldn't be more than one rotation hits for any day, check the dates in your ROTATIONS list.")

    context = {}
    promos = [
        {'name': rotation['name'], 'url': '/', 'template': 'main', 'type': 'cover', 'rotation': rotation},
        {'name': 'Fellesturer', 'url': '/fellesturer/', 'template': 'fellesturer', 'type': 'default'},
        {'name': 'Hytter og ruter', 'url': '/hytter/', 'template': 'hytter', 'type': 'default'},
        {'name': 'Barn', 'url': '/barn/', 'template': 'barn', 'type': 'default'},
        {'name': 'Ungdom', 'url': '/ung/', 'template': 'ung', 'type': 'cover'},
        {'name': 'Fjellsport', 'url': '/fjellsport/', 'template': 'fjellsport', 'type': 'cover'},
        {'name': 'Senior', 'url': '/senior/', 'template': 'senior', 'type': 'default'},
        {'name': 'Skole', 'url': '/skole/', 'template': 'skole', 'type': 'default'},
        {'name': 'Kurs og utdanning', 'url': '/kurs/', 'template': 'kurs', 'type': 'default'},
        {'name': 'Tur for alle', 'url': '/tur-for-alle/', 'template': 'tur-for-alle', 'type': 'default'},
        {'name': 'Turplanlegger', 'url': '/utno/', 'template': 'ut', 'type': 'default'},
        {'name': 'Fjelltreffen', 'url': '/fjelltreffen/', 'type': 'direct'},
    ]

    for promo in promos:
        if path == promo['url'] and promo['type'] != 'direct':
            context['promo'] = {
                'template': 'common/widgets/promo/static/%s.html' % promo['template'],
                'type': promo.get('type'),
            }
            if 'rotation' in promo:
                context['promo'].update({
                    'rotation': promo['rotation'],
                    'rotation_template': 'common/widgets/promo/static/main-rotation/%s.html' % promo['rotation']['id'],
                })

    context['promos'] = promos

    return context
