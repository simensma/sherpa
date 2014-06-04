# encoding: utf-8
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.template import RequestContext
from django.template.loader import render_to_string

from datetime import datetime

from admin.sites.articles.util import BULK_COUNT, list_bulk, create_template, parse_version_content
from articles.models import Article
from page.models import Variant, Version
from page.widgets import widget_admin_context
from user.models import User
from core.models import Site

def list(request, site):
    active_site = Site.objects.get(id=site)
    context = {
        'active_site': active_site,
        'versions': list_bulk(request, 0, active_site),
        'BULK_COUNT': BULK_COUNT,
    }
    return render(request, 'common/admin/sites/articles/list.html', context)

def list_load(request, site):
    active_site = Site.objects.get(id=site)
    if not request.is_ajax():
        return redirect('admin.sites.articles.views.list', active_site.id)
    context = RequestContext(request, {
        'versions': list_bulk(request, int(request.POST['bulk']), active_site),
        'active_site': active_site,
    })
    return HttpResponse(render_to_string('common/admin/sites/articles/list-elements.html', context))

def new(request, site):
    active_site = Site.objects.get(id=site)
    article = Article(
        thumbnail=None,
        hide_thumbnail=False,
        published=False,
        pub_date=None,
        created_by=request.user,
        site=active_site)
    article.save()
    variant = Variant(page=None, article=article, name='default', segment=None, priority=1, owner=request.user)
    variant.save()
    version = Version(variant=variant, version=1, owner=request.user, active=True, ads=False)
    version.save()
    version.publishers.add(request.user)
    create_template(request.POST['template'], version, request.POST['title'])
    return redirect('admin.sites.articles.views.edit', active_site.id, version.id)

def confirm_delete(request, site, article):
    active_site = Site.objects.get(id=site)
    version = Version.objects.get(variant__article=article, variant__segment__isnull=True, active=True)
    context = {
        'active_site': active_site,
        'version': version,
    }
    return render(request, 'common/admin/sites/articles/confirm-delete.html', context)

def delete(request, site, article):
    active_site = Site.objects.get(id=site)
    try:
        Article.objects.get(id=article).delete()
    except Article.DoesNotExist:
        # Probably not a code error but a double-click or something, ignore
        pass
    return redirect('admin.sites.articles.views.list', active_site.id)

def edit(request, site, version):
    active_site = Site.objects.get(id=site)
    rows, version = parse_version_content(request, version, active_site)
    users = sorted(User.sherpa_users(), key=lambda u: u.get_first_name())
    context = {
        'active_site': active_site,
        'rows': rows,
        'version': version,
        'users': users,
        'image_search_length': settings.IMAGE_SEARCH_LENGTH,
        'widget_data': widget_admin_context()
    }
    return render(request, 'common/admin/sites/articles/edit.html', context)

def preview(request, site, version):
    active_site = Site.objects.get(id=site)
    rows, version = parse_version_content(request, version, active_site)
    # Pretend publish date is now, just for the preivew
    version.variant.article.pub_date = datetime.now()
    context = {
        'active_site': active_site,
        'rows': rows,
        'version': version,
    }
    return render(request, 'common/admin/sites/articles/preview.html', context)
