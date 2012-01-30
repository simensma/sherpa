from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Max
from project.page.models import Page, PageVariant, PageVersion, Block, HTMLContent, Widget
from project.analytics.models import Segment
import json

from widgets import *

def new(request, page):
    page = Page.objects.get(pk=page)
    content = PageContent(content="Ny artikkel")
    content.save()
    segment = Segment.objects.get(pk=request.POST['segment'])
    max_priority = PageVariant.objects.filter(page=page).aggregate(Max('priority'))['priority__max']
    variant = PageVariant(page=page, slug=request.POST['slug'], segment=segment, priority=(max_priority+1))
    variant.save()
    version = PageVersion(variant=variant, content=content, version=1, active=True)
    version.save()
    return HttpResponseRedirect(reverse('admin.cms.views.version.edit', args=[version.id]))

def edit(request, version):
    # Not used yet, should be called from page_edit
    return HttpResponseRedirect(reverse('admin.cms.views.version.edit', args=[version]))

def swap(request, page, pri1, pri2):
    variant1 = PageVariant.objects.filter(page=page).get(priority=pri1)
    variant2 = PageVariant.objects.filter(page=page).get(priority=pri2)
    variant1.priority = pri2
    variant2.priority = pri1
    variant1.save()
    variant2.save()
    return HttpResponseRedirect(reverse('admin.cms.views.page.edit', args=[page]))

#def delete(request, variant):
#    variant = PageVariant.objects.get(pk=variant)
#    content = PageContent.objects.get(pagevariant=variant)
#    offset = variant.priority
#    content.delete()
#    variant.delete()
#    # Cascade positions
#    variants = PageVariant.objects.filter(version=variant.version).filter(priority__gt=offset).order_by('priority')
#    for variant in variants:
#        variant.priority = offset
#        variant.save()
#        offset += 1
#    return HttpResponseRedirect(reverse('admin.cms.views.version.edit', args=[variant.version.id]))
