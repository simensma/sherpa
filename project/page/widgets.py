from lxml import etree
import requests
import json
import re

from page.models import Version

BLOG_URL = "http://blogg.turistforeningen.no/feed/"

# Note: This is also imported by some views in admin, and a view in articles
def parse_widget(widget):
    if(widget['widget'] == "quote"):
        data = {'quote': widget['quote'], 'author': widget['author']}
    elif(widget['widget'] == "promo"):
        data = {}
    elif(widget['widget'] == "articles"):
        versions = Version.objects.filter(
            variant__article__isnull=False, variant__segment__isnull=True,
            variant__article__published=True, active=True
            ).order_by('-variant__article__pub_date')[:widget['count']]
        for version in versions:
            version.load_preview()
        data = {'versions': versions}
    elif(widget['widget'] == "blog"):
        r = requests.get(BLOG_URL)
        root = etree.fromstring(r.content)
        entries = []
        for item in root.find('channel').findall('item')[:int(widget['count'])]:
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
        data = {'entries': entries}
    elif(widget['widget'] == "embed"):
        data = {'code': widget['code']}

    data.update({
        'json': json.dumps(widget),
        'template': 'widgets/%s/display.html' % widget['widget'],
        'widget': widget['widget']})
    return data
