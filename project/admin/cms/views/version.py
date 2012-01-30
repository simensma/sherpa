from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Max
from project.page.models import Page, PageVariant, PageVersion, Block, HTMLContent, Widget
from project.analytics.models import Segment
import json

from widgets import *

def new(request, variant):
    variant = PageVariant.objects.get(pk=variant)
    versions = PageVersion.objects.filter(variant=variant)
    max_version = versions.aggregate(Max('version'))['version__max']
    currentVersion = versions.get(version=max_version)
    newContent = PageContent(content=currentVersion.content.content)
    newContent.save()
    version = PageVersion(variant=variant, content=newContent, version=(max_version+1), active=False)
    version.save()
    return HttpResponseRedirect(reverse('admin.views.version_edit', args=[version.id]))

def activate(request, version):
    # Note for future error handling: Fails if activating the _same version_ 2 times in a row (F5)
    newActive = PageVersion.objects.get(pk=version)
    oldActive = PageVersion.objects.filter(variant=newActive.variant).get(active=True)
    newActive.active = True
    oldActive.active = False
    newActive.save()
    oldActive.save()
    return HttpResponseRedirect(reverse('admin.views.version_edit', args=[newActive.id]))

def edit(request, version):
    if(request.method == 'GET'):
        version = PageVersion.objects.get(pk=version)
        blocks = Block.objects.filter(version=version).order_by('order')
        for block in blocks:
            block.template = "admin/page/blocks/%s.html" % block.template
            del block.columns[:]
            block.columns = []
            for i in range(3): # DUPLIKAT AV page/views_widgets.py, fiks
                block.columns.append([])
            # Fetch all items and sort them afterwards
            contents = HTMLContent.objects.filter(block=block)
            widgets = Widget.objects.filter(block=block)
            list = []
            list.extend(contents)
            list.extend(widgets)
            list.sort(key=lambda item: item.order)
            for item in list:
                if isinstance(item, HTMLContent):
                    block.columns[item.column].append({'type': 'html', 'id': item.id, 'content': item.content})
                elif isinstance(item, Widget):
                    widget = json.loads(item.widget)
                    block.columns[item.column].append({'type': 'widget', 'content':
                      parse_widget(item.id, widget)})
        variants = PageVariant.objects.filter(page=version.variant.page).order_by('priority')
        for variant in variants:
            variant.active = PageVersion.objects.get(variant=variant, active=True)
        versions = PageVersion.objects.filter(variant=version.variant).order_by('-version')
        segments = Segment.objects.exclude(name='default')
        context = {'page': version.variant.page, 'variant': version.variant, 'variants': variants,
          'versions': versions, 'version': version, 'segments': segments, 'blocks': blocks}
        return render(request, 'admin/page/edit_variant.html', context)
    elif(request.method == 'POST'):
        version = PageVersion.objects.get(pk=version)
        version.content.content = request.POST['content']
        version.content.save()
        return HttpResponseRedirect(reverse('admin.views.version_edit', args=[version.id]))

