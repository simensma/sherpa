from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect

from page.models import Version, Row, Column, Content
from articles.models import Article

from lxml import etree
import requests
import json
import re

BLOG_URL = "http://blogg.turistforeningen.no/feed/"

def parse_content(request, version):
    rows = Row.objects.filter(version=version).order_by('order')
    for row in rows:
        columns = Column.objects.filter(row=row).order_by('order')
        for column in columns:
            contents = Content.objects.filter(column=column).order_by('order')
            for content in contents:
                if content.type == 'widget':
                    content.content = parse_widget(json.loads(content.content))
                elif content.type == 'image':
                    content.content = json.loads(content.content)
            column.contents = contents
        row.columns = columns
    context = {'rows': rows, 'page': version.variant.page}
    # Used temporary for static promo content
    if request.path == '/':                 context['promo'] = 'widgets/promo/static/sommerapning.html'
    elif request.path == '/fellesturer/':   context['promo'] = 'widgets/promo/static/fellesturer.html'
    elif request.path == '/hytter/':        context['promo'] = 'widgets/promo/static/hytter.html'
    elif request.path == '/barn/':          context['promo'] = 'widgets/promo/static/barn.html'
    elif request.path == '/ung/':           context['promo'] = 'widgets/promo/static/ung.html'
    elif request.path == '/fjellsport/':    context['promo'] = 'widgets/promo/static/fjellsport.html'
    elif request.path == '/senior/':        context['promo'] = 'widgets/promo/static/senior.html'
    elif request.path == '/skole/':         context['promo'] = 'widgets/promo/static/skole.html'
    elif request.path == '/kurs/':          context['promo'] = 'widgets/promo/static/kurs.html'
    elif request.path == '/tur-for-alle/':  context['promo'] = 'widgets/promo/static/tur-for-alle.html'
    return render(request, "page/page.html", context)

# Note: This is also imported by some views in admin, and a view in articles
def parse_widget(widget):
    if(widget['widget'] == "quote"):
        data = {'quote': widget['quote'], 'author': widget['author']}
    elif(widget['widget'] == "promo"):
        data = {}
    elif(widget['widget'] == "editor"):
        article = Article.objects.get(id=widget['article'])
        data = {
            'static': True,
            'author': article.publisher.user.get_full_name(),
            'email': "TBD",
            'publishdate': article.pub_date}
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
            content_truncated = re.sub('<.*?>', '', content)
            image = None
            m = re.search('<img.*?src="(.*?)" ', content)
            if m != None:
                image = m.group(1)
            entries.append({
                'title': item.find('title').text,
                'link': item.find('link').text,
                'content': content_truncated,
                'image': image})
        data = {'entries': entries}
    elif(widget['widget'] == "embed"):
        data = {'code': widget['code']}

    data.update({
        'json': json.dumps(widget),
        'template': 'widgets/%s/display.html' % widget['widget'],
        'widget': widget['widget']})
    return data
