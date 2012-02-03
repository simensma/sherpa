from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from project.page.models import PageVariant, PageVersion, Block, HTMLContent, Widget
from project.analytics.models import Segment
import json

from widget import *

def edit(request, version):
    if(request.method == 'GET'):
        version = PageVersion.objects.get(pk=version)
        blocks = Block.objects.filter(version=version).order_by('order')
        for block in blocks:
            block.template = "admin/cms/editor/advanced/blocks/%s.html" % block.template
            del block.columns[:]
            block.columns = []
            for i in range(3):
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
        return render(request, 'admin/cms/editor/advanced/editor.html', context)
    elif(request.method == 'POST'):
        version = PageVersion.objects.get(pk=version)
        version.content.content = request.POST['content']
        version.content.save()
        return HttpResponseRedirect(reverse('admin.cms.views.editor_advanced.edit', args=[version.id]))

