from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Max
from page.models import Page, PageVariant, PageVersion, Layout, HTMLContent, Widget
from analytics.models import Segment
from django.views.decorators.csrf import csrf_exempt
import json

def page_variant_new(request, page):
    page = Page.objects.get(pk=page)
    content = PageContent(content="Ny artikkel")
    content.save()
    segment = Segment.objects.get(pk=request.POST['segment'])
    max_priority = PageVariant.objects.filter(page=page).aggregate(Max('priority'))['priority__max']
    variant = PageVariant(page=page, slug=request.POST['slug'], segment=segment, priority=(max_priority+1))
    variant.save()
    version = PageVersion(variant=variant, content=content, version=1, active=True)
    version.save()
    return HttpResponseRedirect(reverse('admin.views.page_version_edit', args=[version.id]))

def page_variant_edit(request, version):
    # Not used yet, should be called from page_edit
    return HttpResponseRedirect(reverse('admin.views.page_version_edit', args=[version]))

def page_variant_swap(request, page, pri1, pri2):
    variant1 = PageVariant.objects.filter(page=page).get(priority=pri1)
    variant2 = PageVariant.objects.filter(page=page).get(priority=pri2)
    variant1.priority = pri2
    variant2.priority = pri1
    variant1.save()
    variant2.save()
    return HttpResponseRedirect(reverse('admin.views.page_edit', args=[page]))

def page_version_new(request, variant):
    variant = PageVariant.objects.get(pk=variant)
    versions = PageVersion.objects.filter(variant=variant)
    max_version = versions.aggregate(Max('version'))['version__max']
    currentVersion = versions.get(version=max_version)
    newContent = PageContent(content=currentVersion.content.content)
    newContent.save()
    version = PageVersion(variant=variant, content=newContent, version=(max_version+1), active=False)
    version.save()
    return HttpResponseRedirect(reverse('admin.views.page_version_edit', args=[version.id]))

def page_version_activate(request, version):
    # Note for future error handling: Fails if activating the _same version_ 2 times in a row (F5)
    newActive = PageVersion.objects.get(pk=version)
    oldActive = PageVersion.objects.filter(variant=newActive.variant).get(active=True)
    newActive.active = True
    oldActive.active = False
    newActive.save()
    oldActive.save()
    return HttpResponseRedirect(reverse('admin.views.page_version_edit', args=[newActive.id]))

def page_version_edit(request, version):
    if(request.method == 'GET'):
        version = PageVersion.objects.get(pk=version)
        layouts = Layout.objects.filter(version=version).order_by('order')
        for layout in layouts:
            mode = request.GET.get('mode')
            # Default editmode to layout. Should this really be defined here?
            if(mode != 'layout' and mode != 'content'):
                mode = 'layout'
            layout.template = "admin/page/layouts/%s_%s.html" % (layout.template, mode)
            del layout.columns[:]
            layout.columns = []
            for i in range(3): # DUPLIKAT AV page/views_widgets.py, fiks
                layout.columns.append([])
            # Fetch all items and sort them afterwards
            contents = HTMLContent.objects.filter(layout=layout)
            widgets = Widget.objects.filter(layout=layout)
            list = []
            list.extend(contents)
            list.extend(widgets)
            list.sort(key=lambda item: item.order)
            for item in list:
                if isinstance(item, HTMLContent):
                    layout.columns[item.column].append({'type': 'html', 'id': item.id, 'content': item.content})
                elif isinstance(item, Widget):
                    widget = json.loads(item.widget)
                    layout.columns[item.column].append({'type': 'widget', 'content':
                      parse_widget(widget)})
        variants = PageVariant.objects.filter(page=version.variant.page).order_by('priority')
        for variant in variants:
            variant.active = PageVersion.objects.get(variant=variant, active=True)
        versions = PageVersion.objects.filter(variant=version.variant).order_by('-version')
        segments = Segment.objects.exclude(name='default')
        context = {'page': version.variant.page, 'variant': version.variant, 'variants': variants,
          'versions': versions, 'version': version, 'segments': segments, 'layouts': layouts,
          'mode': mode}
        return render(request, 'admin/page/edit_variant.html', context)
    elif(request.method == 'POST'):
        version = PageVersion.objects.get(pk=version)
        version.content.content = request.POST['content']
        version.content.save()
        return HttpResponseRedirect(reverse('admin.views.page_version_edit', args=[version.id]))

def page_add_layout(request, version, template):
    version = PageVersion.objects.get(id=version)
    # error handling: if there are no layouts (if that's at all possible?), set order to 1
    max = Layout.objects.filter(version=version).aggregate(Max('order'))['order__max']
    layout = Layout(version=version, template=template, order=(max+1))
    layout.save()
    return HttpResponseRedirect(reverse('admin.views.page_version_edit', args=[version.id]))

def parse_widget(widget):
    if(widget['name'] == "foo"):
        return {'template': 'page/widgets/foo.html', 'bar': 'baz'}
    elif(widget['name'] == "memberservice"):
        return {'template': 'page/widgets/memberservice.html'}

# Ajax for content and widgets

@csrf_exempt
def page_content_update(request, content):
    content = HTMLContent.objects.get(id=content)
    content.content = request.POST['content']
    content.save()
    return HttpResponse('')

@csrf_exempt
def page_layout_swap(request, layout1, layout2):
    layout1 = Layout.objects.get(id=layout1)
    layout2 = Layout.objects.get(id=layout2)
    tmp = layout1.order
    layout1.order = layout2.order
    layout2.order = tmp
    layout1.save()
    layout2.save()
    return HttpResponse('')

#def page_variant_delete(request, variant):
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
#    return HttpResponseRedirect(reverse('admin.views.page_version_edit', args=[variant.version.id]))
