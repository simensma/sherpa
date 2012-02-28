from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.conf import settings

import json

from articles.models import Article
from page.models import Variant, Version, Row, Column, Content

from admin.cms.views.widget import parse_widget

@login_required
def list(request):
    versions = Version.objects.filter(variant__article__isnull=False, variant__segment__isnull=True, active=True)
    context = {'versions': versions}
    return render(request, 'admin/articles/list.html', context)

@login_required
def new(request):
    article = Article(title=request.POST['title'], published=False, pub_date=None,
      publisher=request.user.get_profile())
    article.save()
    variant = Variant(page=None, article=article, name='default', segment=None, priority=1, publisher=request.user.get_profile())
    variant.save()
    version = Version(variant=variant, version=1, publisher=request.user.get_profile(), active=True)
    version.save()

    # Save a new article based on this pre-defined template.
    contents = [{'content': """<div class="editable"><h1>Fengende overskrift</h1></div><div class="imgbg"><img class="changeable" src=\"""" + settings.STATIC_URL + """img/article/placeholder-top.png" alt="placeholder"></div><br><div class="editable">BILDETEKST: Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a diam lectus.<br><em>Foto: Ola Nordmann</em></div>""", 'type': 'h'},
        {'content': """<div class="lede editable"><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris. Maecenas congue ligula ac quam viverra nec consectetur ante hendrerit. Donec et mollis dolor. Praesent et diam eget libero egestas mattis sit amet vitae augue. Nam tincidunt congue enim, ut porta lorem lacinia consectetur. Donec ut libero sed arcu vehicula ultricies a non tortor.</p></div>""", 'type': 'h'},
        {'content': """<div class="meta"><hr></div>""", 'type': 'h'},
        {'content': """<div class="meta static"><p><em>(Todo!) Kari Nordmann</em><br><a href="mailto:">redaksjonen@turistforeningen.no</a><br>Publisert 21. august 2012</p></div>""", 'type': 'h'},
        {'content': """<div class="meta"><hr></div>""", 'type': 'h'},
        {'content': """<div class="editable"><p>Vivamus fermentum semper porta. Nunc diam velit, adipiscing ut tristique vitae, sagittis vel odio. Maecenas convallis ullamcorper ultricies. Curabitur ornare, ligula semper consectetur sagittis, nisi diam iaculis velit, id fringilla sem nunc vel mi. Nam dictum, odio nec pretium volutpat, arcu ante placerat erat, non tristique elit urna et turpis. Quisque mi metus, ornare sit amet fermentum et, tincidunt et orci. Fusce eget orci a orci congue vestibulum.</p></div>""", 'type': 'h'},
        {'content': """<div class="image-right"><img class="changeable" src=\"""" + settings.STATIC_URL + """img/article/placeholder-side.png" alt="placeholder"><br><div class="editable">BILDETEKST: Donec ut libero sed arcu vehicula.<br><em>Foto: Kari Nordmann/DNT</em></div></div><div class="editable"><p>Ut dolor diam, elementum et vestibulum eu, porttitor vel elit. Curabitur venenatis pulvinar tellus gravida ornare. Sed et erat faucibus nunc euismod ultricies ut id justo. Nullam cursus suscipit nisi, et ultrices justo sodales nec. Fusce venenatis facilisis lectus ac semper. Aliquam at massa ipsum. Quisque bibendum purus convallis nulla ultrices ultricies. Nullam aliquam, mi eu aliquam tincidunt, purus velit laoreet tortor, viverra pretium nisi quam vitae mi. Fusce vel volutpat elit. Nam sagittis nisi dui.</p><h2>Underoverskrift</h2><p>Suspendisse lectus leo, consectetur in tempor sit amet, placerat quis neque. Etiam luctus porttitor lorem, sed suscipit est rutrum non. Curabitur lobortis nisl a enim congue semper. Aenean commodo ultrices imperdiet. Vestibulum ut justo vel sapien venenatis tincidunt. Phasellus eget dolor sit amet ipsum dapibus condimentum vitae quis lectus. Aliquam ut massa in turpis dapibus convallis. Praesent elit lacus, vestibulum at malesuada et, ornare et est. Ut augue nunc, sodales ut euismod non, adipiscing vitae orci. Mauris ut placerat justo. Mauris in ultricies enim. Quisque nec est eleifend nulla ultrices egestas quis ut quam. Donec sollicitudin lectus a mauris pulvinar id aliquam urna cursus. Cras quis ligula sem, vel elementum mi. Phasellus non ullamcorper urna.</p><p>Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. In euismod ultrices facilisis. Vestibulum porta sapien adipiscing augue congue id pretium lectus molestie. Proin quis dictum nisl. Morbi id quam sapien, sed vestibulum sem. Duis elementum rutrum mauris sed convallis. Proin vestibulum magna mi. Aenean tristique hendrerit magna, ac facilisis nulla hendrerit ut. Sed non tortor sodales quam auctor elementum. Donec hendrerit nunc eget elit pharetra pulvinar. Suspendisse id tempus tortor. Aenean luctus, elit commodo laoreet commodo, justo nisi consequat massa, sed vulputate quam urna quis eros. Donec vel.</p></div>""", 'type': 'h'},
        {'content': """<img class="changeable" src=\"""" + settings.STATIC_URL + """img/article/placeholder-bottom.png" alt="placeholder"><br><div class="editable">BILDETEKST: Donec ut libero sed arcu vehicula.<br><em>Foto: Kari Nordmann/DNT</em></div>""", 'type': 'h'},
    ]

    for i in range(8):
        row = Row(version=version, order=i)
        row.save()
        column = Column(row=row, span=8, offset=2, order=0)
        column.save()
        content = Content(column=column, content=contents[i]['content'], type=contents[i]['type'], order=0)
        content.save()

    return HttpResponseRedirect(reverse('admin.articles.views.edit', args=[version.id]))

@login_required
def edit(request, version):
    version = Version.objects.get(id=version)
    rows = Row.objects.filter(version=version).order_by('order')
    for row in rows:
        columns = Column.objects.filter(row=row).order_by('order')
        for column in columns:
            contents = Content.objects.filter(column=column).order_by('order')
            for content in contents:
                if content.type == 'w':
                    content.widget = parse_widget(json.loads(content.content))
            column.contents = contents
        row.columns = columns
    context = {'rows': rows, 'version': version}
    return render(request, 'admin/articles/edit.html', context)

@login_required
def save(request, version):
    version = Version.objects.get(id=version)
    contents = json.loads(request.POST['contents'])
    for newContent in contents:
        content = Content.objects.get(id=newContent['id'])
        content.content = newContent['content']
        content.save()
    return HttpResponse()
