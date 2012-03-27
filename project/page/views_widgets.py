from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect

from page.models import Row, Column, Content
from articles.models import Article

import json

def parse_content(request, version):
    rows = Row.objects.filter(version=version).order_by('order')
    for row in rows:
        columns = Column.objects.filter(row=row).order_by('order')
        for column in columns:
            contents = Content.objects.filter(column=column).order_by('order')
            for content in contents:
                if content.type == 'w':
                    content.widget = parse_widget(json.loads(content.content))
            column.contents = contents
        row.columns = columns
    context = {'rows': rows, 'page': version.variant.page}
    return render(request, "page/page.html", context)

def parse_widget(widget):
    if(widget['widget'] == "quote"):
        return {'template': 'widgets/quote/display.html', 'quote': widget['quote'], 'author': widget['author']}
    elif(widget['widget'] == "promo"):
        return {'template': 'widgets/promo/display.html'}
    elif(widget['widget'] == "editor"):
        article = Article.objects.get(id=widget['article'])
        return {'template': 'widgets/editor/display.html',
            'author': article.publisher.user.get_full_name(),
            'email': "TBD",
            'publishdate': article.pub_date}
