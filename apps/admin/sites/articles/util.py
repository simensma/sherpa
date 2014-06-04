from django.conf import settings

from page.models import Version, Row, Column, Content
from page.widgets import parse_widget

import json

BULK_COUNT = 8

def list_bulk(request, bulk, active_site):
    return Version.objects.filter(
        variant__article__isnull=False,
        variant__segment__isnull=True,
        active=True,
        variant__article__site=active_site
    ).order_by('-variant__article__created_date')[(bulk * BULK_COUNT) : (bulk * BULK_COUNT) + BULK_COUNT]

def parse_version_content(request, version, active_site):
    version = Version.objects.get(id=version)
    rows = Row.objects.filter(version=version).order_by('order')
    for row in rows:
        columns = Column.objects.filter(row=row).order_by('order')
        for column in columns:
            contents = Content.objects.filter(column=column).order_by('order')
            for content in contents:
                if content.type == 'widget':
                    content.content = parse_widget(request, json.loads(content.content), active_site)
            column.contents = contents
        row.columns = columns
    return rows, version

def create_template(template, version, title):
    if template == '0':
        contents = [
            {'type': 'title', 'content': """<h1>%s</h1>""" % title},
            {'type': 'image', 'content': json.dumps({'src': "http://www.turistforeningen.no" + settings.STATIC_URL + "img/placeholder.png", "description": "", "photographer": "", "anchor": None})},
            {'type': 'lede', 'content': ""},
            {'type': 'html', 'content': ""},
            {'type': 'image', 'content': json.dumps({'src': "http://www.turistforeningen.no" + settings.STATIC_URL + "img/placeholder.png", "description": "", "photographer": "", "anchor": None})},
        ]
        row = Row(version=version, order=0)
        row.save()
        column = Column(row=row, span=12, offset=0, order=0)
        column.save()
        for i in range(len(contents)):
            content = Content(column=column, content=contents[i]['content'], type=contents[i]['type'], order=i)
            content.save()
    elif template == '1':
        contents_upper = [
            {'type': 'title', 'content': """<h1>%s</h1>""" % title},
            {'type': 'image', 'content': json.dumps({'src': "http://www.turistforeningen.no" + settings.STATIC_URL + "img/placeholder.png", "description": "", "photographer": "", "anchor": None})},
            {'type': 'lede', 'content': ""},
        ]
        contents_lower_left = [
            {'type': 'html', 'content': ""},
        ]
        contents_lower_right = [
            {'type': 'html', 'content': ""},
            {'type': 'image', 'content': json.dumps({'src': "http://www.turistforeningen.no" + settings.STATIC_URL + "img/placeholder.png", "description": "", "photographer": "", "anchor": None})},
        ]
        row = Row(version=version, order=0)
        row.save()
        column = Column(row=row, span=12, offset=0, order=0)
        column.save()
        for i in range(len(contents_upper)):
            content = Content(column=column, content=contents_upper[i]['content'], type=contents_upper[i]['type'], order=i)
            content.save()
        row = Row(version=version, order=1)
        row.save()
        column = Column(row=row, span=9, offset=0, order=0)
        column.save()
        for i in range(len(contents_lower_left)):
            content = Content(column=column, content=contents_lower_left[i]['content'], type=contents_lower_left[i]['type'], order=i)
            content.save()
        column = Column(row=row, span=3, offset=0, order=1)
        column.save()
        for i in range(len(contents_lower_right)):
            content = Content(column=column, content=contents_lower_right[i]['content'], type=contents_lower_right[i]['type'], order=i)
            content.save()
