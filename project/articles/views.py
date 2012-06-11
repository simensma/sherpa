from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings

from articles.models import Article
from page.models import Variant, Version, Row, Column, Content
from page.views_widgets import parse_widget

import json

def index(request):
    versions = Version.objects.filter(
        variant__article__isnull=False, variant__segment__isnull=True,
        variant__article__published=True, active=True
        ).order_by('-variant__article__pub_date')[:20]
    for version in versions:
        version.load_preview()
    context = {'versions': versions, 'old_site': settings.OLD_SITE}
    return render(request, "page/articles-list.html", context)

def show(request, article, text):
    # Assume no segmentation for now
    article = Article.objects.get(id=article)
    variant = Variant.objects.get(article=article, segment=None)
    version = Version.objects.get(variant=variant, active=True)
    version.load_preview()
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
    context = {'rows': rows, 'article': article, 'version': version}
    return render(request, "page/article.html", context)
