from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Max
from project.page.models import Page, PageVariant, PageVersion, Layout, HTMLContent, Widget
from project.analytics.models import Segment
import json

from widgets import *

def add(request, version, template):
    version = PageVersion.objects.get(id=version)
    layouts = Layout.objects.filter(version=version)
    if(len(layouts) == 0):
        max = 0
    else:
        max = layouts.aggregate(Max('order'))['order__max']
    layout = Layout(version=version, template=template, order=(max+1))
    layout.save()
    return HttpResponseRedirect(reverse('admin.views.version_edit', args=[version.id]))

def move_up(request, layout):
    layout = Layout.objects.get(id=layout)
    if(layout.order == 1):
        # error handling
        raise Exception
    else:
        swap_layouts(layout, -1)
        return HttpResponseRedirect(reverse('admin.views.version_edit', args=[layout.version.id]))

def move_down(request, layout):
    layout = Layout.objects.get(id=layout)
    max = Layout.objects.filter(version=layout.version).aggregate(Max('order'))['order__max']
    if(layout.order == max):
        # error handling
        raise Exception
    else:
        swap_layouts(layout, 1)
        return HttpResponseRedirect(reverse('admin.views.version_edit', args=[layout.version.id]))

def delete(request, layout):
    layout = Layout.objects.get(id=layout)
    widgets = Widget.objects.filter(layout=layout)
    contents = HTMLContent.objects.filter(layout=layout)
    layout.delete()
    widgets.delete()
    contents.delete()
    return HttpResponseRedirect(reverse('admin.views.version_edit', args=[layout.version.id]))


def swap_layouts(layout, increment):
    other_layout = Layout.objects.get(version=layout.version, order=(layout.order + increment))
    other_layout.order = layout.order
    layout.order = other_layout.order + increment
    other_layout.save()
    layout.save()
