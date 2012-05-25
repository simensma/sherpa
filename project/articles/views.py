from django.shortcuts import render
from django.http import HttpResponse

from articles.models import Article
from page.models import Variant, Version, Row, Column, Content
from page.views_widgets import parse_widget

import json

def index(request):
    return HttpResponse()

def show(request, article, text):
    # Assume no segmentation for now
    article = Article.objects.get(id=article)
    variant = Variant.objects.get(article=article, segment=None)
    version = Version.objects.get(variant=variant, active=True)
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
    return render(request, "page/article.html", context)
