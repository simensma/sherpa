from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.conf import settings

import json

from articles.models import Article
from page.models import Variant, Version, Row, Column, Content

from page.views_widgets import parse_widget

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
    contents = [
        {'type': 'html', 'content': """<h1>Fengende overskrift</h1>"""},
        {'type': 'image', 'content': """<img src=\"""" + settings.STATIC_URL + """img/templates/placeholder.png" alt="placeholder">"""},
        {'type': 'html', 'content': """<p>BILDETEKST: Nunc diam velit, adipiscing ut tristique vitae, sagittis vel odio. Maecenas convallis.<br><em>Foto: Ola Nordmann/DNT</em></p>"""},
        {'type': 'html', 'content': """<div class="lede"><p>Suspendisse lectus leo, consectetur in tempor sit amet, placerat quis neque. Etiam luctus porttitor lorem, sed suscipit est rutrum non. Curabitur lobortis nisl a enim congue semper. Aenean commodo ultrices imperdiet.</p></div>"""},
        {'type': 'widget', 'content': json.dumps({'widget': 'editor', 'article': article.id})},
        {'type': 'html', 'content': """<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris. Maecenas congue ligula ac quam viverra nec consectetur ante hendrerit. Donec et mollis dolor. Praesent et diam eget libero egestas mattis sit amet vitae augue. Nam tincidunt congue enim, ut porta lorem lacinia consectetur. Donec ut libero sed arcu vehicula ultricies a non tortor. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean ut gravida lorem. Ut turpis felis, pulvinar a semper sed, adipiscing id dolor.</p><h2>Vivamus fermentum semper porta.</h2><p>Pellentesque auctor nisi id magna consequat sagittis. Curabitur dapibus enim sit amet elit pharetra tincidunt feugiat nisl imperdiet. Ut convallis libero in urna ultrices accumsan. Donec sed odio eros. Donec viverra mi quis quam pulvinar at malesuada arcu rhoncus. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. In rutrum accumsan ultricies. Mauris vitae nisi at sem facilisis semper ac in est.</p>"""},
        {'type': 'image', 'content': """<img src=\"""" + settings.STATIC_URL + """img/templates/placeholder.png" alt="placeholder">"""},
        {'type': 'html', 'content': """<p>BILDETEKST: Donec ut libero sed arcu vehicula.<br><em>Foto: Kari Nordmann/DNT</em></p>"""},
    ]

    row = Row(version=version, order=0)
    row.save()
    column = Column(row=row, span=8, offset=2, order=0)
    column.save()
    for i in range(len(contents)):
        content = Content(column=column, content=contents[i]['content'], type=contents[i]['type'], order=i)
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
                if content.type == 'widget':
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

@login_required
def delete(request, article):
    Article.objects.get(id=article).delete()
    return HttpResponseRedirect(reverse('admin.articles.views.list'))
