from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.conf import settings

from project.page.models import Menu, Page, Variant, Version, Row, Column, Content

import json

@login_required
def list(request):
    pages = Page.objects.all()
    menus = Menu.objects.all().order_by('order')
    context = {'pages': pages, 'menus': menus, 'site': request.site}
    return render(request, 'admin/pages/list.html', context)

@login_required
def new(request):
    page = Page(title=request.POST['title'], slug=request.POST['slug'], published=False, publisher=request.user.get_profile())
    page.save()
    variant = Variant(page=page, article=None, name='Standard', segment=None, priority=1, publisher=request.user.get_profile())
    variant.save()
    version = Version(variant=variant, version=1, publisher=request.user.get_profile(), active=True)
    version.save()
    if request.POST['template'] == '2':
        contents = [
            {'type': 'html', 'content': """<h1>Fengende overskrift</h1>"""},
            {'type': 'image', 'content': """<img src=\"""" + settings.STATIC_URL + """img/templates/placeholder.jpg" alt="Placeholder">"""},
            {'type': 'html', 'content': """<p>BILDETEKST: Nunc diam velit, adipiscing ut tristique vitae, sagittis vel odio. Maecenas convallis.<br><em>Foto: Ola Nordmann/DNT</em></p>"""},
            {'type': 'html', 'content': """<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris. Maecenas congue ligula ac quam viverra nec consectetur ante hendrerit. Donec et mollis dolor. Praesent et diam eget libero egestas mattis sit amet vitae augue. Nam tincidunt congue enim, ut porta lorem lacinia consectetur. Donec ut libero sed arcu vehicula ultricies a non tortor. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean ut gravida lorem. Ut turpis felis, pulvinar a semper sed, adipiscing id dolor. Pellentesque auctor nisi id magna consequat sagittis. Curabitur dapibus enim sit amet elit pharetra tincidunt feugiat nisl imperdiet. Ut convallis libero in urna ultrices accumsan. Donec sed odio eros. Donec viverra mi quis quam pulvinar at malesuada arcu rhoncus. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. In rutrum accumsan ultricies. Mauris vitae nisi at sem facilisis semper ac in est.</p>"""},
            {'type': 'html', 'content': """<h2>Mindre overskrift</h2><p>Vivamus fermentum semper porta. Nunc diam velit, adipiscing ut tristique vitae, sagittis vel odio. Maecenas convallis ullamcorper ultricies. Curabitur ornare, ligula semper consectetur sagittis, nisi diam iaculis velit, id fringilla sem nunc vel mi. Nam dictum, odio nec pretium volutpat, arcu ante placerat erat, non tristique elit urna et turpis. Quisque mi metus, ornare sit amet fermentum et, tincidunt et orci. Fusce eget orci a orci congue vestibulum. Ut dolor diam, elementum et vestibulum eu, porttitor vel elit. Curabitur venenatis pulvinar tellus gravida ornare. Sed et erat faucibus nunc euismod ultricies ut id justo. Nullam cursus suscipit nisi, et ultrices justo sodales nec. Fusce venenatis facilisis lectus ac semper. Aliquam at massa ipsum. Quisque bibendum purus convallis nulla ultrices ultricies. Nullam aliquam, mi eu aliquam tincidunt, purus velit laoreet tortor, viverra pretium nisi quam vitae mi. Fusce vel volutpat elit. Nam sagittis nisi dui.</p>"""},
            {'type': 'image', 'content': """<img src=\"""" + settings.STATIC_URL + """img/templates/placeholder.jpg" alt="Placeholder">"""},
            {'type': 'html', 'content': """<p>BILDETEKST: Donec ut libero sed arcu vehicula.<br><em>Foto: Kari Nordmann/DNT</em></p>"""},
        ]
        row = Row(version=version, order=0)
        row.save()
        column = Column(row=row, span=12, offset=0, order=0)
        column.save()
        for i in range(len(contents)):
            content = Content(column=column, content=contents[i]['content'], type=contents[i]['type'], order=i)
            content.save()
    return HttpResponseRedirect(reverse('admin.cms.views.version.edit', args=[version.id]))

@login_required
def edit(request, page):
    if request.is_ajax():
        page = Page.objects.get(id=page)
        page.title = request.POST['title']
        page.slug = request.POST['slug']
        page.save()
        return HttpResponse()
    else:
        page = Page.objects.get(id=page)
        version = Version.objects.get(variant__page=page, active=True)
        context = {'page': page, 'version': version, 'site': request.site}
        return render(request, 'admin/pages/edit.html', context)

@login_required
def delete(request, page):
    Page.objects.get(id=page).delete()
    return HttpResponseRedirect(reverse('admin.cms.views.page.list'))
