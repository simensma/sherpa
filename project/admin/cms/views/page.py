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
    create_template(request.POST['template'], version)
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

def create_template(template, version):
    if template == '1':
        # Empty
        return
    elif template == '2':
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
    elif template == '3':
        contents_upper = [
            {'type': 'html', 'content': """<h1>Fengende overskrift</h1>"""},
            {'type': 'image', 'content': """<img src=\"""" + settings.STATIC_URL + """img/templates/placeholder.jpg" alt="Placeholder">"""},
            {'type': 'html', 'content': """<p>BILDETEKST: Nunc diam velit, adipiscing ut tristique vitae, sagittis vel odio. Maecenas convallis.<br><em>Foto: Ola Nordmann/DNT</em></p>"""},
        ]
        contents_lower_left = [
            {'type': 'html', 'content': """<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris. Maecenas congue ligula ac quam viverra nec consectetur ante hendrerit. Donec et mollis dolor. Praesent et diam eget libero egestas mattis sit amet vitae augue. Nam tincidunt congue enim, ut porta lorem lacinia consectetur. Donec ut libero sed arcu vehicula ultricies a non tortor. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean ut gravida lorem. Ut turpis felis, pulvinar a semper sed, adipiscing id dolor. Pellentesque auctor nisi id magna consequat sagittis. Curabitur dapibus enim sit amet elit pharetra tincidunt feugiat nisl imperdiet. Ut convallis libero in urna ultrices accumsan. Donec sed odio eros. Donec viverra mi quis quam pulvinar at malesuada arcu rhoncus. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. In rutrum accumsan ultricies. Mauris vitae nisi at sem facilisis semper ac in est.</p>"""},
            {'type': 'html', 'content': """<h2>Mindre overskrift</h2><p>Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. In euismod ultrices facilisis. Vestibulum porta sapien adipiscing augue congue id pretium lectus molestie. Proin quis dictum nisl. Morbi id quam sapien, sed vestibulum sem. Duis elementum rutrum mauris sed convallis. Proin vestibulum magna mi. Aenean tristique hendrerit magna, ac facilisis nulla hendrerit ut. Sed non tortor sodales quam auctor elementum. Donec hendrerit nunc eget elit pharetra pulvinar. Suspendisse id tempus tortor. Aenean luctus, elit commodo laoreet commodo, justo nisi consequat massa, sed vulputate quam urna quis eros. Donec vel.</p>"""},
        ]
        contents_lower_right = [
            {'type': 'html', 'content': """<p>Suspendisse lectus leo, consectetur in tempor sit amet, placerat quis neque. Etiam luctus porttitor lorem, sed suscipit est rutrum non. Curabitur lobortis nisl a enim congue semper. Aenean commodo ultrices imperdiet. Vestibulum ut justo vel sapien venenatis tincidunt. Phasellus eget dolor sit amet ipsum dapibus condimentum vitae quis lectus.</p>"""},
            {'type': 'image', 'content': """<img src=\"""" + settings.STATIC_URL + """img/templates/placeholder.jpg" alt="Placeholder">"""},
            {'type': 'html', 'content': """<p>BILDETEKST: Donec ut libero sed arcu vehicula.<br><em>Foto: Kari Nordmann/DNT</em></p>"""},
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
            {'type': 'image', 'content': """<img src=\"""" + settings.STATIC_URL + """img/templates/placeholder.jpg" alt="Placeholder">"""},
            {'type': 'html', 'content': """<p>BILDETEKST: Nunc diam velit, adipiscing ut tristique vitae, sagittis vel odio. Maecenas convallis.<br><em>Foto: Ola Nordmann/DNT</em></p>"""},
        ]
        contents_middle_left = [
            {'type': 'html', 'content': """<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris. Maecenas congue ligula ac quam viverra nec consectetur ante hendrerit. Donec et mollis dolor. Praesent et diam eget libero egestas mattis sit amet vitae augue. Nam tincidunt congue enim, ut porta lorem lacinia consectetur. Donec ut libero sed arcu vehicula ultricies a non tortor. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean ut gravida lorem. Ut turpis felis, pulvinar a semper sed, adipiscing id dolor. Pellentesque auctor nisi id magna consequat sagittis. Curabitur dapibus enim sit amet elit pharetra tincidunt feugiat nisl imperdiet. Ut convallis libero in urna ultrices accumsan. Donec sed odio eros. Donec viverra mi quis quam pulvinar at malesuada arcu rhoncus. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. In rutrum accumsan ultricies. Mauris vitae nisi at sem facilisis semper ac in est.</p>"""},
        ]
        contents_middle_center = [
            {'type': 'html', 'content': """<p>Vivamus fermentum semper porta. Nunc diam velit, adipiscing ut tristique vitae, sagittis vel odio. Maecenas convallis ullamcorper ultricies. Curabitur ornare, ligula semper consectetur sagittis, nisi diam iaculis velit, id fringilla sem nunc vel mi. Nam dictum, odio nec pretium volutpat, arcu ante placerat erat, non tristique elit urna et turpis. Quisque mi metus, ornare sit amet fermentum et, tincidunt et orci. Fusce eget orci a orci congue vestibulum. Ut dolor diam, elementum et vestibulum eu, porttitor vel elit. Curabitur venenatis pulvinar tellus gravida ornare. Sed et erat faucibus nunc euismod ultricies ut id justo. Nullam cursus suscipit nisi, et ultrices justo sodales nec. Fusce venenatis facilisis lectus ac semper. Aliquam at massa ipsum. Quisque bibendum purus convallis nulla ultrices ultricies. Nullam aliquam, mi eu aliquam tincidunt, purus velit laoreet tortor, viverra pretium nisi quam vitae mi. Fusce vel volutpat elit. Nam sagittis nisi dui.</p>"""},
        ]
        contents_middle_right = [
            {'type': 'html', 'content': """<p>Suspendisse lectus leo, consectetur in tempor sit amet, placerat quis neque. Etiam luctus porttitor lorem, sed suscipit est rutrum non. Curabitur lobortis nisl a enim congue semper. Aenean commodo ultrices imperdiet. Vestibulum ut justo vel sapien venenatis tincidunt. Phasellus eget dolor sit amet ipsum dapibus condimentum vitae quis lectus. Aliquam ut massa in turpis dapibus convallis. Praesent elit lacus, vestibulum at malesuada et, ornare et est. Ut augue nunc, sodales ut euismod non, adipiscing vitae orci. Mauris ut placerat justo. Mauris in ultricies enim. Quisque nec est eleifend nulla ultrices egestas quis ut quam. Donec sollicitudin lectus a mauris pulvinar id aliquam urna cursus. Cras quis ligula sem, vel elementum mi. Phasellus non ullamcorper urna.</p>"""},
        ]
        contents_lower = [
            {'type': 'image', 'content': """<img src=\"""" + settings.STATIC_URL + """img/templates/placeholder.jpg" alt="Placeholder">"""},
            {'type': 'html', 'content': """<p>BILDETEKST: Donec ut libero sed arcu vehicula.<br><em>Foto: Kari Nordmann/DNT</em></p>"""},
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
