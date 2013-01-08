from __future__ import absolute_import

from django.http import HttpResponse
from django.template import RequestContext, loader

from page.models import Version, Row, Column, Content
from page.widgets import parse_widget

import json

def add(request):
    if request.is_ajax():
        column = Column.objects.get(id=request.POST['column'])
        for content in Content.objects.filter(column=column, order__gte=request.POST['order']):
            content.order = content.order + 1
            content.save()
        content = Content(column=column, content=request.POST['content'], type=request.POST['type'],
            order=request.POST['order'])
        content.save()
        if content.type == 'html' or content.type == 'image':
            result = content.content
        else:
            widget = parse_widget(request, json.loads(content.content))
            t = loader.get_template(widget['template'])
            c = RequestContext(request, {'widget': widget})
            result = t.render(c)
        return HttpResponse(json.dumps({'id': content.id, 'content': result, 'json': content.content}))

def delete(request, content):
    if request.is_ajax():
        try:
            content = Content.objects.get(id=content)
            content.delete()
        except Content.DoesNotExist:
            # Ignore; it's being deleted anyway
            pass
        return HttpResponse()

def update_widget(request, widget):
    widget = Content.objects.get(id=widget)
    widget.content = request.POST['content']
    widget.save()
    widget = parse_widget(request, json.loads(widget.content))
    t = loader.get_template(widget['template'])
    c = RequestContext(request, {'widget': widget})
    result = t.render(c)
    return HttpResponse(json.dumps({'content': result, 'json': request.POST['content']}))

def save(request, version):
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
