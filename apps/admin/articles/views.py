# encoding: utf-8
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings

from datetime import datetime
import json

from articles.models import Article
from page.models import Variant, Version, Row, Column, Content
from page.widgets import parse_widget, widget_admin_context
from user.models import Profile
from core.models import Tag

import urllib

def list(request):
    versions = Version.objects.filter(
        variant__article__isnull=False,
        variant__segment__isnull=True,
        active=True,
        variant__article__site=request.session['active_association'].site
        ).order_by('-variant__article__created')
    for version in versions:
        version.load_preview()
    context = {'versions': versions}
    return render(request, 'common/admin/articles/list.html', context)

def new(request):
    article = Article(thumbnail=None, hide_thumbnail=False, published=False, pub_date=None, site=request.session['active_association'].site)
    article.save()
    variant = Variant(page=None, article=article, name='default', segment=None, priority=1, owner=request.user.get_profile())
    variant.save()
    version = Version(variant=variant, version=1, owner=request.user.get_profile(), active=True, ads=False)
    version.save()
    version.publishers.add(request.user.get_profile())
    create_template(request.POST['template'], version, request.POST['title'])
    return HttpResponseRedirect(reverse('admin.articles.views.edit_version', args=[version.id]))

def image(request, article):
    article = Article.objects.get(id=article)
    article.thumbnail = request.POST['thumbnail']
    article.hide_thumbnail = False
    article.save()
    return HttpResponse()

def image_delete(request, article):
    article = Article.objects.get(id=article)
    article.thumbnail = None
    article.hide_thumbnail = False
    article.save()
    return HttpResponse()

def image_hide(request, article):
    article = Article.objects.get(id=article)
    article.hide_thumbnail = True
    article.save()
    return HttpResponse()

def publish(request, article):
    datetime_string = urllib.unquote_plus(request.POST["datetime"])
    status =  urllib.unquote_plus(request.POST["status"])

    #date format is this one (dd.mm.yyyy hh:mm)
    try:
        date_object = datetime.strptime(datetime_string, '%d.%m.%Y %H:%M')
    except:
        #datetime could not be parsed, this means the field was empty(default) or corrupted, use now()
        date_object = None

    article = Article.objects.get(id=article)
    article.published = json.loads(status)["status"]
    if date_object is None:
        article.pub_date = datetime.now()
    else:
        article.pub_date = date_object
    article.save()
    return HttpResponse()

def confirm_delete(request, article):
    version = Version.objects.get(variant__article=article, variant__segment__isnull=True, active=True)
    version.load_preview()
    context = {'version': version}
    return render(request, 'common/admin/articles/confirm-delete.html', context)

def delete(request, article):
    Article.objects.get(id=article).delete()
    return HttpResponseRedirect(reverse('admin.articles.views.list'))

def edit_version(request, version):
    rows, version = parse_version_content(request, version)
    profiles = Profile.objects.all().order_by('user__first_name')
    context = {
        'rows': rows,
        'version': version,
        'profiles': profiles,
        'image_search_length': settings.IMAGE_SEARCH_LENGTH,
        'widget_data': widget_admin_context()}
    return render(request, 'common/admin/articles/edit_version.html', context)

def preview(request, version):
    rows, version = parse_version_content(request, version)
    # Pretend publish date is now, just for the preivew
    version.variant.article.pub_date = datetime.now()
    context = {'rows': rows, 'version': version}
    return render(request, 'common/admin/articles/preview.html', context)

def parse_version_content(request, version):
    version = Version.objects.get(id=version)
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
    return rows, version

def update_publishers(request, version):
    version = Version.objects.get(id=version)
    publisher_list = json.loads(request.POST['authors'])
    publishers = Profile.objects.filter(id__in=publisher_list)
    version.publishers = publishers
    return HttpResponse()

def update_tags(request, version):
    version = Version.objects.get(id=version)
    tag_objects = []
    for tag in json.loads(request.POST['tags']):
        try:
            tag_obj = Tag.objects.get(name__iexact=tag)
        except Tag.DoesNotExist:
            tag_obj = Tag(name=tag)
            tag_obj.save()
        tag_objects.append(tag_obj)
    version.tags = tag_objects
    return HttpResponse()

def create_template(template, version, title):
    if template == '0':
        contents = [
            {'type': 'title', 'content': """<h1>%s</h1>""" % title},
            {'type': 'image', 'content': json.dumps({'src': settings.STATIC_URL + "img/placeholder.png", "description": "", "photographer": "", "anchor": None})},
            {'type': 'lede', 'content': """<p class="lede"><br></p>"""},
            {'type': 'html', 'content': """<p><br></p>"""},
            {'type': 'image', 'content': json.dumps({'src': settings.STATIC_URL + "img/placeholder.png", "description": "", "photographer": "", "anchor": None})},
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
            {'type': 'image', 'content': json.dumps({'src': settings.STATIC_URL + "img/placeholder.png", "description": "", "photographer": "", "anchor": None})},
            {'type': 'lede', 'content': """<p class="lede"><br></p>"""},
        ]
        contents_lower_left = [
            {'type': 'html', 'content': """<p><br></p>"""},
        ]
        contents_lower_right = [
            {'type': 'html', 'content': """<p><br></p>"""},
            {'type': 'image', 'content': json.dumps({'src': settings.STATIC_URL + "img/placeholder.png", "description": "", "photographer": "", "anchor": None})},
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
