from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.core.cache import cache

from articles.models import Article
from page.models import AdPlacement, Variant, Version, Row, Column, Content
from page.widgets import parse_widget
import datetime

import json

def index(request):
    versions = Version.objects.filter(
        variant__article__isnull=False, variant__segment__isnull=True,
        variant__article__published=True, active=True, variant__article__pub_date__lt=datetime.datetime.now()
        ).order_by('-variant__article__pub_date')[:20]
    for version in versions:
        version.load_preview()
    context = {'versions': versions}
    return render(request, "page/articles-list.html", context)

def show(request, article, text):
    context = cache.get('articles.%s' % article)
    if context == None:
        # Assume no segmentation for now
        try:
            article = Article.objects.get(id=article)
            variant = Variant.objects.get(article=article, segment=None)
            version = Version.objects.get(variant=variant, active=True)
        except (Article.DoesNotExist, Variant.DoesNotExist, Version.DoesNotExist):
            raise Http404
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
        context = {'rows': rows, 'version': version}
        cache.set('articles.%s' % article.id, context, 60 * 10)
    context['ad'] = AdPlacement.get_active_ad('articles')
    return render(request, "page/article.html", context)
