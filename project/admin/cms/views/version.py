from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Max
from django.contrib.auth.decorators import login_required

from project.page.views_widgets import *
from project.page.models import Variant, Version, Row, Column, Content

import json

@login_required
def new(request, variant):
    variant = Variant.objects.get(id=variant)
    versions = Version.objects.filter(variant=variant)
    max_version = versions.aggregate(Max('version'))['version__max']
    currentVersion = versions.get(version=max_version)
    newContent = PageContent(content=currentVersion.content.content)
    newContent.save()
    version = Version(variant=variant, content=newContent, version=(max_version+1), publisher=request.user.get_profile(), active=False)
    version.save()
    return HttpResponseRedirect(reverse('admin.cms.views.version.edit', args=[version.id]))

@login_required
def edit(request, version):
    if request.method == 'GET':
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
