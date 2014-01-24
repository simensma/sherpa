# encoding: utf-8
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.core.cache import cache

from datetime import datetime

from page.models import *

from instagram.views import initial_url as instagram_initial_url

def index(request):
    page_versions = Version.objects.filter(
        variant__page__isnull=False,
        active=True
        ).order_by('variant__page__title')

    article_versions = Version.objects.filter(
        variant__article__isnull=False,
        variant__segment__isnull=True,
        variant__article__published=True,
        active=True,
        variant__article__pub_date__lt=datetime.now(),
        variant__article__site=request.session['active_forening'].site
        ).order_by('-variant__article__pub_date')

    for version in article_versions:
        version.load_preview()

    context = {
        'article_versions': article_versions,
        'page_versions': page_versions
    }
    return render(request, 'common/admin/cache/index.html', context)

def delete(request):
    if not request.is_ajax():
        return redirect('admin.cache.views.index')

    if request.POST['key'] == 'frontpage':
        id = Version.objects.get(
            active=True,
            variant__segment__isnull=True,
            variant__page__slug='',
            variant__page__site=request.session['active_forening'].site
            ).id
        cache.delete('content.version.%s' % id)
    elif request.POST['key'] == 'page':
        cache.delete('content.version.%s' % request.POST['id'])
    elif request.POST['key'] == 'article':
        cache.delete('articles.%s' % request.POST['id'])
    elif request.POST['key'] == 'main-menu':
        cache.delete('main.menu')
    elif request.POST['key'] == 'blog-widget':
        cache.delete('widgets.blog.category.Alle')
        # Chances are, this was done to show it on the frontpage, so just delete the frontpage-cache too since it's cached twice.
        id = Version.objects.get(active=True, variant__segment__isnull=True, variant__page__slug='').id
        cache.delete('content.version.%s' % id)
    elif request.POST['key'] == 'instagram':
        cache.delete('instagram.url.%s' % instagram_initial_url)
    return HttpResponse()
