from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

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
    return HttpResponseRedirect(reverse('admin.articles.views.edit', args=[version.id]))

@login_required
def edit(request, version):
    version = Version.objects.get(id=version)
    rows = Row.objects.filter(version=version).order_by('order')
    if(len(rows) == 0):
        context = {'version': version}
        return render(request, 'admin/articles/edit.template.html', context)
    for row in rows:
        columns = Column.objects.filter(row=row).order_by('order')
        for column in columns:
            contents = Content.objects.filter(column=column).order_by('order')
            for content in contents:
                if content.type == 'w':
                    content.widget = parse_widget(json.loads(content.content))
            column.contents = contents
        row.columns = columns
    context = {'rows': rows}
    return render(request, 'admin/articles/edit.existing.html', context)

@login_required
def save(request, version):
    version = Version.objects.get(id=version)
    if(request.POST['template'] == "true"):
        rows = json.loads(request.POST['json'])
        rowOrder = 0
        for rowObj in rows['rows']:
            row = Row(version=version, order=rowOrder)
            row.save()
            rowOrder += 1
            colOrder = 0
            for colObj in rowObj['columns']:
                col = Column(row=row, span=colObj['span'], offset=colObj['offset'], order=colOrder)
                col.save()
                content = Content(column=col, content=colObj['content'], type='h', order=colOrder)
                content.save()
                colOrder += 1
    else:
        # Todo: Update instead of save
        return HttpResponse()
    return HttpResponse()
