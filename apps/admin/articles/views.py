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

BULK_COUNT = 8

def list(request):
    context = {
        'versions': list_bulk(request, 0),
        'BULK_COUNT': BULK_COUNT,
    }
    return render(request, 'common/admin/articles/list.html', context)

def list_load(request):
    if not request.is_ajax():
        return redirect('admin.articles.views.list')
    context = RequestContext(request, {'versions': list_bulk(request, int(request.POST['bulk']))})
    return HttpResponse(render_to_string('common/admin/articles/list-elements.html', context))

# This is not a view.
def list_bulk(request, bulk):
    return Version.objects.filter(
        variant__article__isnull=False,
        variant__segment__isnull=True,
        active=True,
        variant__article__site=request.active_forening.site
    ).order_by('-variant__article__created_date')[(bulk * BULK_COUNT) : (bulk * BULK_COUNT) + BULK_COUNT]

def new(request):
    article = Article(
        thumbnail=None,
        hide_thumbnail=False,
        published=False,
        pub_date=None,
        created_by=request.user,
        site=request.active_forening.site)
    article.save()
    variant = Variant(page=None, article=article, name='default', segment=None, priority=1, owner=request.user)
    variant.save()
    version = Version(variant=variant, version=1, owner=request.user, active=True, ads=False)
    version.save()
    version.publishers.add(request.user)
    create_template(request.POST['template'], version, request.POST['title'])
    return redirect('admin.articles.views.edit', version.id)

def confirm_delete(request, article):
    version = Version.objects.get(variant__article=article, variant__segment__isnull=True, active=True)
    context = {'version': version}
    return render(request, 'common/admin/articles/confirm-delete.html', context)

def delete(request, article):
    try:
        Article.objects.get(id=article).delete()
    except Article.DoesNotExist:
        # Probably not a code error but a double-click or something, ignore
        pass
    return redirect('admin.articles.views.list')

def edit(request, version):
    rows, version = parse_version_content(request, version)
    users = sorted(User.sherpa_users(), key=lambda u: u.get_first_name())
    context = {
        'rows': rows,
        'version': version,
        'users': users,
        'image_search_length': settings.IMAGE_SEARCH_LENGTH,
        'widget_data': widget_admin_context()
    }
    return render(request, 'common/admin/articles/edit.html', context)

def preview(request, version):
    rows, version = parse_version_content(request, version)
    # Pretend publish date is now, just for the preivew
    version.variant.article.pub_date = datetime.now()
    context = {'rows': rows, 'version': version}
    return render(request, 'common/admin/articles/preview.html', context)

def parse_version_content(request, version):
    version = Version.objects.get(id=version)
    rows = Row.objects.filter(version=version).order_by('order')
    for row in rows:
        columns = Column.objects.filter(row=row).order_by('order')
        for column in columns:
            contents = Content.objects.filter(column=column).order_by('order')
            for content in contents:
                if content.type == 'widget':
                    content.content = parse_widget(request, json.loads(content.content), request.active_forening.site)
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
