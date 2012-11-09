from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.core.cache import cache
from django.template import RequestContext, loader

from articles.models import Article
from page.models import AdPlacement, Variant, Version, Row, Column, Content
from page.widgets import parse_widget
import datetime

import json

TAG_SEARCH_LENGTH = 3
NEWS_ITEMS_BULK_SIZE = 20 # Needs to be an even number!

def index(request):
    versions = Version.objects.filter(
        variant__article__isnull=False, variant__segment__isnull=True,
        variant__article__published=True, active=True, variant__article__pub_date__lt=datetime.datetime.now()
        ).order_by('-variant__article__pub_date')

    tags = request.GET.getlist('tag')
    if 'tag' in request.GET and len(request.GET['tag']) >= TAG_SEARCH_LENGTH:
        versions = versions.filter(tags__name__icontains=request.GET['tag'])

    versions = versions[:NEWS_ITEMS_BULK_SIZE]
    for version in versions:
        version.load_preview()
    context = {'versions': versions, 'tag': request.GET.get('tag', ''),
        'advertisement': AdPlacement.get_active_ad()}
    return render(request, "page/articles-list.html", context)

# Note: This is probably not compatible with the tag search
def more(request):
    response = []
    print(request.POST['current'])
    versions = Version.objects.filter(
        variant__article__isnull=False, variant__segment__isnull=True,
        variant__article__published=True, active=True, variant__article__pub_date__lt=datetime.datetime.now()
        ).order_by('-variant__article__pub_date')[request.POST['current']:int(request.POST['current']) + NEWS_ITEMS_BULK_SIZE]
    for version in versions:
        version.load_preview()
        t = loader.get_template('page/article-list-item.html')
        c = RequestContext(request, {'version': version})
        response.append(t.render(c))
    return HttpResponse(json.dumps(response))

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
    context['advertisement'] = AdPlacement.get_active_ad()
    return render(request, "page/article.html", context)
