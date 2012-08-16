from django.core.cache import cache

from lxml import etree
import requests
import json
import re
import random
import datetime

from page.models import Version

BLOG_URL = "http://blogg.turistforeningen.no/"

# Note: This is also imported by some views in admin, and a view in articles
def parse_widget(widget):
    if widget['widget'] == "quote":
        data = {'quote': widget['quote'], 'author': widget['author']}
    elif widget['widget'] == 'carousel':
        # NO! BAD HAVARD, dont use hax, create an id(but not now)
        data = {'id':random.randint(0,10000), 'images':widget['images']}
    elif widget['widget'] == "articles":
        versions = Version.objects.filter(
            variant__article__isnull=False, variant__segment__isnull=True,
            variant__article__published=True, active=True, variant__article__pub_date__lt=datetime.datetime.now()
            ).order_by('-variant__article__pub_date')[:widget['count']]
        for version in versions:
            version.load_preview()
        data = {'versions': versions}
    elif widget['widget'] == "blog":
        # This is a pretty heavy query, so cache it for a while
        data = cache.get('widgets.blog' + widget['category'])
        if data == None:

            feed_url = BLOG_URL;

            if widget['category'] != 'Alle':
                feed_url += 'tema/' + widget['category'].lower()
            feed_url += '/feed/'

            try:
                r = requests.get(feed_url)
                channel = etree.fromstring(r.content).find('channel')
            except requests.ConnectionError:
                channel = None

            entries = []
            entries_matched = 0;
            if channel != None:
                for item in channel.findall('item'):

                    item_categories = []
                    for item_category in item.findall('category'):
                        item_categories.append(item_category.text)

                    if (widget['category'] in item_categories or widget['category'] == 'Alle'):
                        entries_matched += 1;

                        content = item.find('{http://purl.org/rss/1.0/modules/content/}encoded').text
                        image = None
                        m = re.search('<img.*?src="(.*?)" ', content)
                        if m != None:
                            image = m.group(1)
                        entries.append({
                            'title': item.find('title').text,
                            'link': item.find('link').text,
                            'content': content,
                            'image': image})
                    if entries_matched >= int(widget['count']):
                        break
            data = {'entries':entries}
            cache.set('widgets.blog' + widget['category'], data, 60 * 10)
    elif widget['widget'] == "embed":
        data = {'code': widget['code']}

    data.update({
        'json': json.dumps(widget),
        'template': 'widgets/%s/display.html' % widget['widget'],
        'widget': widget['widget']})
    return data
