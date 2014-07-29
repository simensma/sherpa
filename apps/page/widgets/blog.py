import requests
import re
import json

from django.core.cache import cache
from django.conf import settings

from lxml import etree

from page.widgets.widget import Widget

class BlogWidget(Widget):
    def parse(self, widget_options, site):
        # This is a pretty heavy query, so cache it for a while
        data = cache.get('widgets.blog.category.' + widget_options['category'])
        if data is None:

            feed_url = "http://%s/" % settings.BLOG_URL;

            if widget_options['category'] != 'Alle':
                feed_url += 'tema/' + widget_options['category'].lower() + '/'
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

                    if (widget_options['category'] in item_categories or widget_options['category'] == 'Alle'):
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
                    if entries_matched >= int(widget_options['count']):
                        break
            data = {'entries':entries}
            cache.set('widgets.blog.category.' + widget_options['category'], data, 60 * 30)
        return data

    def admin_context(self, site):
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
        return {'categories': categories}
