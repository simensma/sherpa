from django.shortcuts import render
from django.core.cache import cache

from datetime import datetime
from lxml import etree
import requests
import re

def index(request):
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

    context = {'betablog': betablog}
    return render(request, 'common/admin/dashboard.html', context)

def intro(request):
    return render(request, 'common/admin/intro.html')
