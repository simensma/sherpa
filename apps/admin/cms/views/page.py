from __future__ import absolute_import

from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.core.urlresolvers import resolve, Resolver404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.core.cache import cache

from page.widgets import parse_widget, widget_admin_context, get_static_promo_context
from page.models import Menu, Page, Variant, Version, Row, Column, Content

from datetime import datetime
import json
import requests

def list(request):
    versions = Version.objects.filter(
        variant__page__isnull=False,
        variant__page__parent__isnull=True,
        active=True,
        variant__page__site=request.session['active_association'].site
        ).order_by('variant__page__title')
    for version in versions:
        version.children = Version.objects.filter(variant__page__parent=version.variant.page, active=True).count()
    menus = Menu.on(request.session['active_association'].site).all().order_by('order')
    context = {'versions': versions, 'menus': menus}
    return render(request, 'common/admin/pages/list.html', context)

def children(request, page):
    versions = Version.objects.filter(variant__page__parent=page, active=True).order_by('variant__page__title')
    for version in versions:
        version.children = Version.objects.filter(variant__page__parent=version.variant.page, active=True).count()
    context = RequestContext(request, {'versions': versions, 'level': request.POST['level']})
    return HttpResponse(render_to_string('common/admin/pages/result.html', context))

def new(request):
    if not slug_is_unique(request.POST['slug']):
        # TODO: Error handling
        raise Exception("Slug is not unique (error handling TBD)")

    page = Page(
        title=request.POST['title'],
        slug=request.POST['slug'],
        published=False,
        created_by=request.user.get_profile(),
        site=request.session['active_association'].site)
    page.save()

    variant = Variant(
        page=page,
        article=None,
        name='Standard',
        segment=None,
        priority=1,
        owner=request.user.get_profile())
    variant.save()

    version = Version(
        variant=variant,
        version=1,
        owner=request.user.get_profile(),
        active=True,
        ads=True)
    version.save()

    create_template(request.POST['template'], version)
    return redirect('admin.cms.views.page.edit_version', version.id)

def check_slug(request):
    urls_valid = slug_is_unique(request.POST['slug'])
    page_valid = not Page.on(request.session['active_association'].site).filter(slug=request.POST['slug']).exists()
    return HttpResponse(json.dumps({'valid': urls_valid and page_valid}))

def delete(request, page):
    Page.on(request.session['active_association'].site).get(id=page).delete()
    return redirect('admin.cms.views.page.list')

def edit_version(request, version):
    pages = Page.on(request.session['active_association'].site).all().order_by('title')
    version = Version.objects.get(id=version)
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
    context = {
        'rows': rows,
        'version': version,
        'widget_data': widget_admin_context(),
        'pages': pages,
        'image_search_length': settings.IMAGE_SEARCH_LENGTH}
    return render(request, 'common/admin/pages/edit_version.html', context)

def preview(request, version):
    version = Version.objects.get(id=version)
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
    if request.site.domain == 'www.turistforeningen.no':
        context.update(get_static_promo_context('/%s/' % version.variant.page.slug))
    return render(request, 'common/admin/pages/preview.html', context)

### Methods - not views - below ###

def slug_is_unique(slug):
    # Verify against the root 'folder' path
    i = slug.find('/')
    if i != -1:
        slug = slug[:i]
    try:
        match = resolve('/%s%s' % (slug, '' if len(slug) == 0 else '/'))
        return match.url_name == 'page.views.page'
    except Resolver404:
        return True

def create_template(template, version):
    if template == '1':
        # Empty
        return
    elif template == '2':
        contents = [
            {'type': 'html', 'content': """<h1>Fengende overskrift</h1>"""},
            {'type': 'image', 'content': json.dumps({'src': settings.STATIC_URL + "img/placeholder.png", 'alt': "placeholder"})},
            {'type': 'html', 'content': """<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris. Maecenas congue ligula ac quam viverra nec consectetur ante hendrerit. Donec et mollis dolor. Praesent et diam eget libero egestas mattis sit amet vitae augue. Nam tincidunt congue enim, ut porta lorem lacinia consectetur. Donec ut libero sed arcu vehicula ultricies a non tortor. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean ut gravida lorem. Ut turpis felis, pulvinar a semper sed, adipiscing id dolor. Pellentesque auctor nisi id magna consequat sagittis. Curabitur dapibus enim sit amet elit pharetra tincidunt feugiat nisl imperdiet. Ut convallis libero in urna ultrices accumsan. Donec sed odio eros. Donec viverra mi quis quam pulvinar at malesuada arcu rhoncus. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. In rutrum accumsan ultricies. Mauris vitae nisi at sem facilisis semper ac in est.</p>"""},
            {'type': 'html', 'content': """<h2>Mindre overskrift</h2><p>Vivamus fermentum semper porta. Nunc diam velit, adipiscing ut tristique vitae, sagittis vel odio. Maecenas convallis ullamcorper ultricies. Curabitur ornare, ligula semper consectetur sagittis, nisi diam iaculis velit, id fringilla sem nunc vel mi. Nam dictum, odio nec pretium volutpat, arcu ante placerat erat, non tristique elit urna et turpis. Quisque mi metus, ornare sit amet fermentum et, tincidunt et orci. Fusce eget orci a orci congue vestibulum. Ut dolor diam, elementum et vestibulum eu, porttitor vel elit. Curabitur venenatis pulvinar tellus gravida ornare. Sed et erat faucibus nunc euismod ultricies ut id justo. Nullam cursus suscipit nisi, et ultrices justo sodales nec. Fusce venenatis facilisis lectus ac semper. Aliquam at massa ipsum. Quisque bibendum purus convallis nulla ultrices ultricies. Nullam aliquam, mi eu aliquam tincidunt, purus velit laoreet tortor, viverra pretium nisi quam vitae mi. Fusce vel volutpat elit. Nam sagittis nisi dui.</p>"""},
            {'type': 'image', 'content': json.dumps({'src': settings.STATIC_URL + "img/placeholder.png", 'alt': "placeholder"})},
        ]
        row = Row(version=version, order=0)
        row.save()
        column = Column(row=row, span=12, offset=0, order=0)
        column.save()
        for i in range(len(contents)):
            content = Content(column=column, content=contents[i]['content'], type=contents[i]['type'], order=i)
            content.save()
    elif template == '3':
        contents_upper = [
            {'type': 'html', 'content': """<h1>Fengende overskrift</h1>"""},
            {'type': 'image', 'content': json.dumps({'src': settings.STATIC_URL + "img/placeholder.png", 'alt': "placeholder"})},
        ]
        contents_lower_left = [
            {'type': 'html', 'content': """<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris. Maecenas congue ligula ac quam viverra nec consectetur ante hendrerit. Donec et mollis dolor. Praesent et diam eget libero egestas mattis sit amet vitae augue. Nam tincidunt congue enim, ut porta lorem lacinia consectetur. Donec ut libero sed arcu vehicula ultricies a non tortor. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean ut gravida lorem. Ut turpis felis, pulvinar a semper sed, adipiscing id dolor. Pellentesque auctor nisi id magna consequat sagittis. Curabitur dapibus enim sit amet elit pharetra tincidunt feugiat nisl imperdiet. Ut convallis libero in urna ultrices accumsan. Donec sed odio eros. Donec viverra mi quis quam pulvinar at malesuada arcu rhoncus. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. In rutrum accumsan ultricies. Mauris vitae nisi at sem facilisis semper ac in est.</p>"""},
            {'type': 'html', 'content': """<h2>Mindre overskrift</h2><p>Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. In euismod ultrices facilisis. Vestibulum porta sapien adipiscing augue congue id pretium lectus molestie. Proin quis dictum nisl. Morbi id quam sapien, sed vestibulum sem. Duis elementum rutrum mauris sed convallis. Proin vestibulum magna mi. Aenean tristique hendrerit magna, ac facilisis nulla hendrerit ut. Sed non tortor sodales quam auctor elementum. Donec hendrerit nunc eget elit pharetra pulvinar. Suspendisse id tempus tortor. Aenean luctus, elit commodo laoreet commodo, justo nisi consequat massa, sed vulputate quam urna quis eros. Donec vel.</p>"""},
        ]
        contents_lower_right = [
            {'type': 'html', 'content': """<p>Suspendisse lectus leo, consectetur in tempor sit amet, placerat quis neque. Etiam luctus porttitor lorem, sed suscipit est rutrum non. Curabitur lobortis nisl a enim congue semper. Aenean commodo ultrices imperdiet. Vestibulum ut justo vel sapien venenatis tincidunt. Phasellus eget dolor sit amet ipsum dapibus condimentum vitae quis lectus.</p>"""},
            {'type': 'image', 'content': json.dumps({'src': settings.STATIC_URL + "img/placeholder.png", 'alt': "placeholder"})},
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
        column = Column(row=row, span=3, offset=0, order=0)
        column.save()
        for i in range(len(contents_lower_right)):
            content = Content(column=column, content=contents_lower_right[i]['content'], type=contents_lower_right[i]['type'], order=i)
            content.save()
    elif template == '4':
        contents_upper = [
            {'type': 'html', 'content': """<h1>Fengende overskrift</h1>"""},
            {'type': 'image', 'content': json.dumps({'src': settings.STATIC_URL + "img/placeholder.png", 'alt': "placeholder"})},
        ]
        contents_middle_left = [
            {'type': 'html', 'content': """<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris. Maecenas congue ligula ac quam viverra nec consectetur ante hendrerit. Donec et mollis dolor. Praesent et diam eget libero egestas mattis sit amet vitae augue. Nam tincidunt congue enim, ut porta lorem lacinia consectetur. Donec ut libero sed arcu vehicula ultricies a non tortor. Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>"""},
        ]
        contents_middle_center = [
            {'type': 'html', 'content': """<p>Vivamus fermentum semper porta. Nunc diam velit, adipiscing ut tristique vitae, sagittis vel odio. Maecenas convallis ullamcorper ultricies. Curabitur ornare, ligula semper consectetur sagittis, nisi diam iaculis velit, id fringilla sem nunc vel mi. Nam dictum, odio nec pretium volutpat, arcu ante placerat erat, non tristique elit urna et turpis. Quisque mi metus, ornare sit amet fermentum et, tincidunt et orci. Fusce eget orci a orci congue vestibulum.</p>"""},
        ]
        contents_middle_right = [
            {'type': 'html', 'content': """<p>Vivamus fermentum semper porta. Nunc diam velit, adipiscing ut tristique vitae, sagittis vel odio. Maecenas convallis ullamcorper ultricies. Curabitur ornare, ligula semper consectetur sagittis, nisi diam iaculis velit, id fringilla sem nunc vel mi. Nam dictum, odio nec pretium volutpat, arcu ante placerat erat, non tristique elit urna et turpis. Quisque mi metus, ornare sit amet fermentum et, tincidunt et orci. Fusce eget orci a orci congue vestibulum.</p>"""},
        ]
        contents_lower = [
            {'type': 'image', 'content': json.dumps({'src': settings.STATIC_URL + "img/placeholder.png", 'alt': "placeholder"})},
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
        column = Column(row=row, span=4, offset=0, order=0)
        column.save()
        for i in range(len(contents_middle_left)):
            content = Content(column=column, content=contents_middle_left[i]['content'], type=contents_middle_left[i]['type'], order=i)
            content.save()
        column = Column(row=row, span=4, offset=0, order=1)
        column.save()
        for i in range(len(contents_middle_center)):
            content = Content(column=column, content=contents_middle_center[i]['content'], type=contents_middle_center[i]['type'], order=i)
            content.save()
        column = Column(row=row, span=4, offset=0, order=2)
        column.save()
        for i in range(len(contents_middle_right)):
            content = Content(column=column, content=contents_middle_right[i]['content'], type=contents_middle_right[i]['type'], order=i)
            content.save()
        row = Row(version=version, order=2)
        row.save()
        column = Column(row=row, span=12, offset=0, order=0)
        column.save()
        for i in range(len(contents_lower)):
            content = Content(column=column, content=contents_lower[i]['content'], type=contents_lower[i]['type'], order=i)
            content.save()
