# encoding: utf-8
from datetime import datetime, date
import json
import re
import random

from django.core.cache import cache
from django.conf import settings
from django.template import RequestContext
from django.template.loader import render_to_string

from lxml import etree
import requests

from page.models import Version
from admin.models import Campaign

def render_widget(request, widget_options, current_site, admin_context=False, include_container=True, content_id=None):
    """Returns a string with the given widget rendered, ready for display.

    admin_context can be set to True to wrap the rendered widget in the appropriate container, and to tell
    the widget to display extra information to the admin-user if appropriate.

    include_container can be set to False to exclude the containing element from the rendered html if
    the caller wants to handle that manually (typically when a widget is saved in the admin UI)

    content_id needs to be set if both admin_context and include_container is True as the admin container needs access
    to the content id
    """
    widget = parse_widget(request, widget_options, current_site)
    context = RequestContext(request, {
        'widget': widget,
        'admin_context': admin_context,
        'include_container': include_container,
        'content_id': content_id,
    })
    return render_to_string('common/widgets/container.html', context)

def parse_widget(request, widget, current_site):
    """
    Parse the supplied widget, perform the server-side view logic and return the final widget
    data context for rendering in its template
    """
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
            variant__article__site=current_site,
        ).order_by('-variant__article__pub_date')

        if len(widget['tags']) == 0:
            version_matches = versions
        else:
            # Filter on tags. We'll have to do multiple queries, since we can't make list-lookups with 'icontains'.
            # The alternative would be some sort of advanced regex.
            version_matches = []
            for tag in widget['tags']:
                for version in versions.filter(tags__name__icontains=tag):
                    # Drop duplicates manually
                    if not version in version_matches:
                        version_matches.append(version)

            # Now re-apply the date sorting, since picking out matches in the order of the tags will mess that up
            version_matches = sorted(version_matches, key=lambda v: v.variant.article.pub_date, reverse=True)

        if widget['layout'] == 'medialist':
            version_matches = version_matches[:int(widget['count'])]
            span = None
        else:
            version_matches = version_matches[:int(widget['columns'])]
            span = 12 / int(widget['columns'])

        data = {
            'layout': widget['layout'],
            'title': widget['title'],
            'display_images': widget['display_images'],
            'tag_link': widget['tag_link'],
            'versions': version_matches,
            'span': span,
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
    elif widget['widget'] == "button":
        data = {
            'text': widget['text'],
            'url': widget['url'],
            'color': widget['color'],
            'size': widget['size'],
        }
    elif widget['widget'] == "table":
        data = {
            'header': widget['table'][0],
            'body': widget['table'][1:],
        }
    elif widget['widget'] == "campaign":
        now = datetime.now()
        active_campaign = None
        for campaign in widget['campaigns']:
            start_date = datetime.strptime(campaign['start_date'], "%d.%m.%Y")
            stop_date = datetime.strptime("%s 23:59:59" % campaign['stop_date'], "%d.%m.%Y %H:%M:%S")

            if widget['hide_when_expired'] and now >= start_date and now <= stop_date:
                active_campaign = campaign
            elif not widget['hide_when_expired'] and now >= start_date:
                active_campaign = campaign

        if active_campaign is None:
            data = {}
        else:
            data = {
                'campaign': Campaign.objects.get(id=active_campaign['campaign_id']),
            }

    data.update({
        'json': json.dumps(widget),
        'template': 'common/widgets/%s/display.html' % widget['widget'],
        'widget': widget['widget'],
    })
    return data


def widget_admin_context():
    """
    Returns a dict for each widget which needs database in the admin-editor context. Will be available in the editors
    through 'widget_data.<widget>'
    """
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
        'blog': {'categories': blog_category_list()},
        'campaigns': Campaign.objects.all(),
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
            'end_date': date(year=2013, month=12, day=18),
        },
        {
            'id': 'godjul',
            'name': 'God jul',
            'start_date': date(year=2013, month=12, day=19),
            'end_date': date(year=2013, month=12, day=31),
        },
        {
            'id': 'godtnyttar',
            'name': 'Godt nytt turår',
            'start_date': date(year=2014, month=1, day=1),
            'end_date': date(year=2014, month=1, day=12),
        },
        {
            'id': 'kom-deg-ut-feb',
            'name': 'Kom deg ut',
            'start_date': date(year=2014, month=1, day=13),
            'end_date': date(year=2014, month=2, day=2),
        },
        {
            'id': 'vintereventyr',
            'name': 'Vintereventyr',
            'start_date': date(year=2014, month=2, day=3),
            'end_date': date(year=2014, month=4, day=2),
        },
        {
            'id': 'pasketur',
            'name': 'Påsketur',
            'start_date': date(year=2014, month=4, day=3),
            'end_date': date(year=2014, month=4, day=23),
        },
        {
            'id': 'fotokonkurranse',
            'name': 'Fotokonkurranse',
            'start_date': date(year=2014, month=4, day=24),
            'end_date': date(year=2014, month=6, day=3),
        },
        {
            'id': 'sommer',
            'name': 'Sommer',
            'start_date': date(year=2014, month=6, day=4),
            'end_date': date(year=2014, month=6, day=19),
        },
        {
            'id': 'favoritthytter',
            'name': 'Favoritthytter',
            'start_date': date(year=2014, month=6, day=20),
            'end_date': date(year=2014, month=6, day=23),
        },
        {
            'id': 'sommerapning',
            'name': 'Sommeråpning',
            'start_date': date(year=2014, month=6, day=24),
            'end_date': date(year=2014, month=6, day=28),
        },
        {
            'id': 'favoritthytter',
            'name': 'Favoritthytter',
            'start_date': date(year=2014, month=6, day=29),
            'end_date': date(year=2014, month=6, day=29),
        },
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
