from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.template.loader import render_to_string

from articles.models import Article, OldArticle
from page.models import AdPlacement, Variant, Version, Row, Column, Content
from page.widgets import parse_widget

from datetime import datetime
import json

TAG_SEARCH_LENGTH = 3
NEWS_ITEMS_BULK_SIZE = 20 # Needs to be an even number!

def index(request):
    versions = Version.objects.filter(
        variant__article__isnull=False,
        variant__segment__isnull=True,
        variant__article__published=True,
        active=True,
        variant__article__pub_date__lt=datetime.now(),
        variant__article__site=request.site
    ).order_by('-variant__article__pub_date')

    if 'tag' in request.GET and len(request.GET['tag']) >= TAG_SEARCH_LENGTH:
        versions = versions.filter(tags__name__icontains=request.GET['tag'])

    versions = versions[:NEWS_ITEMS_BULK_SIZE]
    for version in versions:
        version.load_preview()
    context = {'versions': versions, 'tag': request.GET.get('tag', '')}
    return render(request, 'common/page/articles-list.html', context)

# Note: This is probably not compatible with the tag search
def more(request):
    if not 'current' in request.POST:
        return HttpResponseRedirect(reverse('articles.views.index'))

    response = []
    versions = Version.objects.filter(
        variant__article__isnull=False,
        variant__segment__isnull=True,
        variant__article__published=True,
        active=True,
        variant__article__pub_date__lt=datetime.now(),
        variant__article__site=request.site
    ).order_by('-variant__article__pub_date')[request.POST['current']:int(request.POST['current']) + NEWS_ITEMS_BULK_SIZE]
    for version in versions:
        version.load_preview()
        context = RequestContext(request, {'version': version})
        response.append(render_to_string('common/page/article-list-item.html', context))
    return HttpResponse(json.dumps(response))

def more_old(request):
    if request.site.domain != 'www.turistforeningen.no':
        return HttpResponse(json.dumps('local_site'))

    response = []
    articles = OldArticle.objects.all().order_by('-date')[request.POST['current']:int(request.POST['current']) + NEWS_ITEMS_BULK_SIZE]
    for article in articles:
        context = RequestContext(request, {'article': article})
        response.append(render_to_string('common/page/article-list-old-item.html', context))
    return HttpResponse(json.dumps(response))

def show(request, article, text):
    context = cache.get('articles.%s' % article)
    if context is None:
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
                        content.content = parse_widget(request, json.loads(content.content))
                    elif content.type == 'image':
                        content.content = json.loads(content.content)
                column.contents = contents
            row.columns = columns
        context = {'rows': rows, 'version': version}
        cache.set('articles.%s' % article.id, context, 60 * 10)
    return render(request, 'common/page/article.html', context)


def show_old(request, article, text):
    # TODO - HACK:
    # Redirect this specific old article to the updated content page, to avoid confusing users
    # (The search currently presents this article in such a way that it's more likely to be
    # clicked than the relevant page when searching for the appropriate keywords)
    if article == '1151':
        return HttpResponseRedirect('/vintermerking/')

    context = cache.get('old_articles.%s' % article)
    if context is None:
        # Assume no segmentation for now
        try:
            article = OldArticle.objects.get(id=article)
            # Age will be cached and incorrect, but since its usage is based on years, and old articles are opened rarely, it's okay.
            age_years = (datetime.now() - article.date).days / 365
            context = {'article': article, 'age_years': age_years}
            cache.set('old_articles.%s' % article.id, context, 60 * 60 * 24 * 30)
        except OldArticle.DoesNotExist:
            raise Http404
    return render(request, 'common/page/article_old.html', context)
