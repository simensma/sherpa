from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from project.page.models import Variant, Version, Row, Column, Content
from project.analytics.models import Segment
import json

from widget import *

@login_required
def edit(request, version):
    if(request.method == 'GET'):
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
        context = {'rows': rows}
        return render(request, 'admin/cms/editor/advanced/editor.html', context)
    elif(request.method == 'POST'):
        version = Version.objects.get(id=version)
        version.content.content = request.POST['content']
        version.content.save()
        return HttpResponseRedirect(reverse('admin.cms.views.editor_advanced.edit', args=[version.id]))
