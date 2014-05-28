# encoding: utf-8
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.template import RequestContext
from django.template.loader import render_to_string

from datetime import datetime
import json

from articles.models import Article
from page.models import Variant, Version, Row, Column, Content
from page.widgets import parse_widget, widget_admin_context
from user.models import User
from core.models import Site

BULK_COUNT = 8

def list(request, site):
    active_site = Site.objects.get(id=site)
    context = {
        'active_site': active_site,
        'versions': list_bulk(request, 0),
        'BULK_COUNT': BULK_COUNT,
    }
    return render(request, 'common/admin/sites/articles/list.html', context)

def list_load(request, site):
    active_site = Site.objects.get(id=site)
    if not request.is_ajax():
        return redirect('admin.sites.articles.views.list', active_site.id)
    context = RequestContext(request, {'versions': list_bulk(request, int(request.POST['bulk']))})
    return HttpResponse(render_to_string('common/admin/sites/articles/list-elements.html', context))

# This is not a view.
def list_bulk(request, site, bulk):
    active_site = Site.objects.get(id=site)
    return Version.objects.filter(
        variant__article__isnull=False,
        variant__segment__isnull=True,
        active=True,
        variant__article__site=active_site
    ).order_by('-variant__article__created_date')[(bulk * BULK_COUNT) : (bulk * BULK_COUNT) + BULK_COUNT]

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
    try:
        Article.objects.get(id=article).delete()
    except Article.DoesNotExist:
        # Probably not a code error but a double-click or something, ignore
        pass
    return redirect('admin.sites.articles.views.list', active_site.id)

def edit(request, site, version):
    active_site = Site.objects.get(id=site)
    rows, version = parse_version_content(request, version)
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
    rows, version = parse_version_content(request, version)
    # Pretend publish date is now, just for the preivew
    version.variant.article.pub_date = datetime.now()
    context = {
        'active_site': active_site,
        'rows': rows,
        'version': version,
    }
    return render(request, 'common/admin/sites/articles/preview.html', context)

def parse_version_content(request, site, version):
    active_site = Site.objects.get(id=site)
    version = Version.objects.get(id=version)
    rows = Row.objects.filter(version=version).order_by('order')
    for row in rows:
        columns = Column.objects.filter(row=row).order_by('order')
        for column in columns:
            contents = Content.objects.filter(column=column).order_by('order')
            for content in contents:
                if content.type == 'widget':
                    content.content = parse_widget(request, json.loads(content.content), active_site)
            column.contents = contents
        row.columns = columns
    return rows, version

def create_template(template, version, title):
    if template == '0':
        contents = [
            {'type': 'title', 'content': """<h1>%s</h1>""" % title},
            {'type': 'image', 'content': json.dumps({'src': "http://www.turistforeningen.no" + settings.STATIC_URL + "img/placeholder.png", "description": "", "photographer": "", "anchor": None})},
            {'type': 'lede', 'content': ""},
            {'type': 'html', 'content': ""},
            {'type': 'image', 'content': json.dumps({'src': "http://www.turistforeningen.no" + settings.STATIC_URL + "img/placeholder.png", "description": "", "photographer": "", "anchor": None})},
        ]
        row = Row(version=version, order=0)
        row.save()
        column = Column(row=row, span=12, offset=0, order=0)
        column.save()
        for i in range(len(contents)):
            content = Content(column=column, content=contents[i]['content'], type=contents[i]['type'], order=i)
            content.save()
    elif template == '1':
        contents_upper = [
            {'type': 'title', 'content': """<h1>%s</h1>""" % title},
            {'type': 'image', 'content': json.dumps({'src': "http://www.turistforeningen.no" + settings.STATIC_URL + "img/placeholder.png", "description": "", "photographer": "", "anchor": None})},
            {'type': 'lede', 'content': ""},
        ]
        contents_lower_left = [
            {'type': 'html', 'content': ""},
        ]
        contents_lower_right = [
            {'type': 'html', 'content': ""},
            {'type': 'image', 'content': json.dumps({'src': "http://www.turistforeningen.no" + settings.STATIC_URL + "img/placeholder.png", "description": "", "photographer": "", "anchor": None})},
        ]
        row = Row(version=version, order=0)
        row.save()
        column = Column(row=row, span=12, offset=0, order=0)
        column.save()
        for i in range(len(contents_upper)):
            content = Content(column=column, content=contents_upper[i]['content'], type=contents_upper[i]['type'], order=i)
            content.save()
        row = Row(version=version, order=1)
        row.save()
        column = Column(row=row, span=9, offset=0, order=0)
        column.save()
        for i in range(len(contents_lower_left)):
            content = Content(column=column, content=contents_lower_left[i]['content'], type=contents_lower_left[i]['type'], order=i)
            content.save()
        column = Column(row=row, span=3, offset=0, order=1)
        column.save()
        for i in range(len(contents_lower_right)):
            content = Content(column=column, content=contents_lower_right[i]['content'], type=contents_lower_right[i]['type'], order=i)
            content.save()
