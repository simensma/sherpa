from __future__ import absolute_import

from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.urlresolvers import resolve, Resolver404
from django.template import Context, loader
from django.core.cache import cache

from page.widgets import parse_widget
from page.models import Menu, Page, Variant, Version, Row, Column, Content

import json

#return the list of categories to use in the blogwidget, can and should be replaced with wordpress jsonapi
def category_list():
    return ['Alle', 'Barn', 'Dugnad', 'Folkehelse', 'Naturforvaltning', 'Skole', 'Ungdom']

@login_required
def list(request):
    versions = Version.objects.filter(variant__page__isnull=False, variant__page__parent__isnull=True, active=True).order_by('variant__page__title')
    for version in versions:
        version.children = Version.objects.filter(variant__page__parent=version.variant.page, active=True).count()
    menus = Menu.objects.all().order_by('order')
    context = {'versions': versions, 'menus': menus, 'site': request.site}
    return render(request, 'admin/pages/list.html', context)

@login_required
def children(request, page):
    versions = Version.objects.filter(variant__page__parent=page, active=True).order_by('variant__page__title')
    for version in versions:
        version.children = Version.objects.filter(variant__page__parent=version.variant.page, active=True).count()
    t = loader.get_template('admin/pages/result.html')
    c = Context({'versions': versions, 'level': request.POST['level']})
    return HttpResponse(t.render(c))

@login_required
def new(request):
    if not slug_is_unique(request.POST['slug']):
        # TODO: Error handling
        raise Exception
    page = Page(title=request.POST['title'], slug=request.POST['slug'], published=False, publisher=request.user.get_profile())
    page.save()
    variant = Variant(page=page, article=None, name='Standard', segment=None, priority=1, publisher=request.user.get_profile())
    variant.save()
    version = Version(variant=variant, version=1, publisher=request.user.get_profile(), active=True)
    version.save()
    create_template(request.POST['template'], version)
    return HttpResponseRedirect(reverse('admin.cms.views.page.edit_version', args=[version.id]))

@login_required
def check_slug(request):
    urls_valid = slug_is_unique(request.POST['slug'])
    page_valid = not Page.objects.filter(slug=request.POST['slug']).exists()
    return HttpResponse(json.dumps({'valid': urls_valid and page_valid}))

@login_required
def rename(request, page):
    page = Page.objects.get(id=page)
    page.title = request.POST['title']
    page.save()
    return HttpResponse()

@login_required
def parent(request, page):
    page = Page.objects.get(id=page)
    if request.POST['parent'] == 'None':
        new_parent = None
    else:
        new_parent = Page.objects.get(id=request.POST['parent'])
        parent = new_parent
        while parent != None:
            if parent.id == page.id:
                return HttpResponse(json.dumps({'error': 'parent_in_parent'}))
            parent = parent.parent
    page.parent = new_parent
    page.save()
    return HttpResponse('{}')

@login_required
def delete(request, page):
    Page.objects.get(id=page).delete()
    return HttpResponseRedirect(reverse('admin.cms.views.page.list'))

@login_required
def edit_version(request, version):
    if request.method == 'GET':
        pages = Page.objects.all().order_by('title')
        version = Version.objects.get(id=version)
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
        context = {'rows': rows, 'version': version, 'categories':category_list(), 'pages': pages}
        return render(request, 'admin/pages/edit_version.html', context)
    elif request.method == 'POST' and request.is_ajax():
        version = Version.objects.get(id=version)
        for row in json.loads(request.POST['rows']):
            obj = Row.objects.get(id=row['id'])
            obj.order = row['order']
            obj.save()
        for column in json.loads(request.POST['columns']):
            obj = Column.objects.get(id=column['id'])
            obj.order = column['order']
            obj.save()
        for content in json.loads(request.POST['contents']):
            obj = Content.objects.get(id=content['id'])
            obj.order = content['order']
            obj.content = content['content']
            obj.save()
        return HttpResponse()

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
