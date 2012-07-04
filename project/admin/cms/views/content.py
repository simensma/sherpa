from __future__ import absolute_import

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import Context, loader

from page.models import Column, Content
from page.widgets import parse_widget

import json

@login_required
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
            widget = parse_widget(json.loads(content.content))
            t = loader.get_template(widget['template'])
            c = Context({'widget': widget})
            result = t.render(c)
        return HttpResponse(json.dumps({'id': content.id, 'content': result, 'json': content.content}))

@login_required
def delete(request, content):
    if request.is_ajax():
        try:
            content = Content.objects.get(id=content)
            content.delete()
        except Content.DoesNotExist:
            # Ignore; it's being deleted anyway
            pass
        return HttpResponse()

@login_required
def update_widget(request, widget):
    widget = Content.objects.get(id=widget)
    widget.content = request.POST['content']
    widget.save()
    widget = parse_widget(json.loads(widget.content))
    t = loader.get_template(widget['template'])
    c = Context({'widget': widget})
    result = t.render(c)
    return HttpResponse(json.dumps({'content': result, 'json': request.POST['content']}))
