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
            layout.template = "admin/page/layouts/%s.html" % layout.template
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
          'versions': versions, 'version': version, 'segments': segments, 'layouts': layouts}
        return render(request, 'admin/page/edit_variant.html', context)
    elif(request.method == 'POST'):
        version = PageVersion.objects.get(pk=version)
        version.content.content = request.POST['content']
        version.content.save()
        return HttpResponseRedirect(reverse('admin.views.page_version_edit', args=[version.id]))

def page_add_layout(request, version, template):
    version = PageVersion.objects.get(id=version)
    layouts = Layout.objects.filter(version=version)
    if(len(layouts) == 0):
        max = 0
    else:
        max = layouts.aggregate(Max('order'))['order__max']
    layout = Layout(version=version, template=template, order=(max+1))
    layout.save()
    return HttpResponseRedirect(reverse('admin.views.page_version_edit', args=[version.id]))

def page_layout_move_up(request, layout):
    layout = Layout.objects.get(id=layout)
    if(layout.order == 1):
        # error handling
        raise Exception
    else:
        swap_layouts(layout, -1)
        return HttpResponseRedirect(reverse('admin.views.page_version_edit', args=[layout.version.id]))

def page_layout_move_down(request, layout):
    layout = Layout.objects.get(id=layout)
    max = Layout.objects.filter(version=layout.version).aggregate(Max('order'))['order__max']
    if(layout.order == max):
        # error handling
        raise Exception
    else:
        swap_layouts(layout, 1)
        return HttpResponseRedirect(reverse('admin.views.page_version_edit', args=[layout.version.id]))

def page_layout_delete(request, layout):
    layout = Layout.objects.get(id=layout)
    widgets = Widget.objects.filter(layout=layout)
    contents = HTMLContent.objects.filter(layout=layout)
    layout.delete()
    widgets.delete()
    contents.delete()
    return HttpResponseRedirect(reverse('admin.views.page_version_edit', args=[layout.version.id]))


def swap_layouts(layout, increment):
    other_layout = Layout.objects.get(version=layout.version, order=(layout.order + increment))
    other_layout.order = layout.order
    layout.order = other_layout.order + increment
    other_layout.save()
    layout.save()

def parse_widget(widget):
    if(widget['name'] == "quote"):
        return {'template': 'admin/page/widgets/quote.html'}

def page_version_add_widget_quote(request, version):
    layout = Layout.objects.get(id=request.POST['layout'])
    widget = Widget(layout=layout, widget=json.dumps({"name": "quote"}),
      column=request.POST['column'], order=request.POST['order'])
    widget.save()
    request.method = "GET" # Small hack for the page_version_edit method
    return page_version_edit(request, version)

# Ajax for content and widgets

@csrf_exempt
def page_content_create(request, layout, column, order):
    layout = Layout.objects.get(id=layout)
    content = HTMLContent(layout=layout, content=request.POST['content'], column=column, order=order)
    content.save()
    return HttpResponse(json.dumps({'id': content.id}))

@csrf_exempt
def page_content_update(request, content):
    content = HTMLContent.objects.get(id=content)
    content.content = request.POST['content']
    content.save()
    return HttpResponse(json.dumps({'id': content.id}))

@csrf_exempt
def page_content_delete(request, content):
    content = HTMLContent.objects.get(id=content)
    content.delete()
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
