from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Max
from project.page.models import Page, PageVariant, PageVersion, Block, HTMLContent, Widget
from project.analytics.models import Segment
import json

from widget import *

def create(request):
    block = Block.objects.get(id=request.POST['block'])
    content = HTMLContent(block=block, content="<p>Nytt innhold...</p>",
        column=request.POST['column'], order=request.POST['order'])
    content.save()
    return HttpResponseRedirect(reverse('admin.views.version_edit', args=[block.version.id]))

def update(request, content):
    content = HTMLContent.objects.get(id=content)
    content.content = request.POST['content']
    content.save()
    return HttpResponse('')

def delete(request, content):
    content = HTMLContent.objects.get(id=content)
    content.delete()
    if(request.is_ajax()):
        return HttpResponse('')
    else:
        return HttpResponseRedirect(reverse('admin.views.version_edit', args=[content.block.version.id]))
