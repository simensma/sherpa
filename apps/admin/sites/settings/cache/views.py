# encoding: utf-8
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.cache import cache

from datetime import datetime

from page.models import *
from core.models import Site

from instagram.views import initial_url as instagram_initial_url

def index(request, site):
    active_site = Site.objects.get(id=site)
    page_versions = Version.objects.filter(
        variant__page__isnull=False,
        active=True,
    ).order_by('variant__page__title')

    article_versions = Version.objects.filter(
        variant__article__isnull=False,
        variant__segment__isnull=True,
        variant__article__published=True,
        active=True,
        variant__article__pub_date__lt=datetime.now(),
        variant__article__site=active_site,
    ).order_by('-variant__article__pub_date')

    context = {
        'active_site': active_site,
        'article_versions': article_versions,
        'page_versions': page_versions,
    }
    return render(request, 'common/admin/sites/settings/cache/index.html', context)

def delete(request, site):
    active_site = Site.objects.get(id=site)
    if not request.is_ajax():
        return redirect('admin.sites.settings.cache.views.index', active_site.id)

    if request.POST['key'] == 'frontpage':
        id = Version.objects.get(
            active=True,
            variant__segment__isnull=True,
            variant__page__slug='',
            variant__page__site=active_site,
        ).id
        cache.delete('content.version.%s' % id)
    elif request.POST['key'] == 'page':
        cache.delete('content.version.%s' % request.POST['id'])
    elif request.POST['key'] == 'article':
        cache.delete('articles.%s' % request.POST['id'])
        version = Version.objects.get(variant__article__id=request.POST['id'])
        cache.delete('version.%s.thumbnail.small' % version.id)
        cache.delete('version.%s.thumbnail.medium' % version.id)
    elif request.POST['key'] == 'blog-widget':
        cache.delete('widgets.blog.category.Alle')
        # Chances are, this was done to show it on the frontpage, so just delete the frontpage-cache too since it's cached twice.
        id = Version.objects.get(
            active=True,
            variant__segment__isnull=True,
            variant__page__slug='',
            variant__page__site=active_site,
        ).id
        cache.delete('content.version.%s' % id)
    elif request.POST['key'] == 'instagram':
        cache.delete('instagram.url.%s' % instagram_initial_url)
    return HttpResponse()
