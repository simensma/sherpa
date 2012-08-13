# encoding: utf-8
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.cache import cache

from datetime import datetime

from page.models import *

@login_required
def index(request):
    versions = Version.objects.filter(
        variant__article__isnull=False, variant__segment__isnull=True,
        variant__article__published=True, active=True, variant__article__pub_date__lt=datetime.now()
        ).order_by('-variant__article__pub_date')
    for version in versions:
        version.load_preview()
    context = {'versions': versions}
    return render(request, 'admin/cache/index.html', context)

@login_required
def delete(request):
    if not request.is_ajax():
        return HttpResponseRedirect(reverse('admin.cache.views.index'))

    if request.POST['key'] == 'frontpage':
        id = Version.objects.get(active=True, variant__segment__isnull=True, variant__page__slug='').id
        cache.delete('content.version.%s' % id)
    elif request.POST['key'] == 'article':
        cache.delete('articles.%s' % request.POST['article'])
    return HttpResponse()
