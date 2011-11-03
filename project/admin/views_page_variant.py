from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.db.models import Max
from page.models import Page
from page.models import PageVersion
from page.models import PageContent
from analytics.models import PageVariant
from analytics.models import Segment

def page_variant_new(request, version):
    if(request.method == 'GET'):
        version = PageVersion.objects.get(pk=version)
        versions = PageVersion.objects.filter(page=version.page).order_by('-version')
        variants = PageVariant.objects.filter(version=version).order_by('priority')
        segments = Segment.objects.all()
        active = versions.get(active=True)
        context = {'active': active, 'version': version, 'versions': versions, 'variants': variants,
          'segments': segments}
        return render(request, 'admin/page/edit_variant.html', context)
    elif(request.method == 'POST'):
        version = PageVersion.objects.get(pk=version)
        content = PageContent(content=request.POST['content'])
        content.save()
        segment = Segment.objects.get(pk=request.POST['segment'])
        # Find the highest priority and assign 1 higher (or 1 if none exists)
        max_priority = PageVariant.objects.filter(version=version).aggregate(Max('priority'))['priority__max']
        if(max_priority is None):
            max_priority = 0
        variant = PageVariant(version=version, content=content, slug=request.POST['slug'],
          segment=segment, priority=(max_priority+1))
        variant.save()
        return HttpResponseRedirect(reverse('admin.views.page_version_edit', args=[version.id]))

#def variant_edit(request, page):
#    if(request.method == 'GET'):
#        try:
#            page = Page.objects.get(pk=page)
#            context = {'page': page}
#            return render(request, 'admin/page/edit.html', context)
#        except (KeyError, Page.DoesNotExist):
#            return page_list(request, error="This page does not exist.")
#    elif(request.method == 'POST'):
#        try:
#            page = Page.objects.get(pk=page)
#            page.active.content = request.POST['content']
#            page.slug = request.POST['slug']
#            page.active.save()
#            page.save()
#            return HttpResponseRedirect(reverse('admin.views.page_list'))
#        except (KeyError, Page.DoesNotExist):
#            content = PageContent(version=1.0, content=request.POST['content'])
#            page = Page(active=content, slug=request.POST['slug'])
#            context = {'page': page, 'error': "Whoops, looks like you tried to edit a non-existing thing."}
#            return render(request, 'admin/page/edit.html', context)
#

def page_variant_swap(request, version, pri1, pri2):
    variant1 = PageVariant.objects.filter(version=version).get(priority=pri1)
    variant2 = PageVariant.objects.filter(version=version).get(priority=pri2)
    variant1.priority = pri2
    variant2.priority = pri1
    variant1.save()
    variant2.save()
    return HttpResponseRedirect(reverse('admin.views.page_version_edit', args=[version]))

def page_variant_delete(request, variant):
    variant = PageVariant.objects.get(pk=variant)
    content = PageContent.objects.get(pagevariant=variant)
    offset = variant.priority
    content.delete()
    variant.delete()
    # Cascade positions
    variants = PageVariant.objects.filter(version=variant.version).filter(priority__gt=offset).order_by('priority')
    for variant in variants:
        variant.priority = offset
        variant.save()
        offset += 1
    return HttpResponseRedirect(reverse('admin.views.page_version_edit', args=[variant.version.id]))
