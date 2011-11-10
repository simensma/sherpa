from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.db.models import Max
from page.models import Page, PageVariant, PageVersion, PageContent
from analytics.models import Segment

def page_variant_new(request, page):
    page = Page.objects.get(pk=page)
    content = PageContent(content="Ny artikkel")
    content.save()
    segment = Segment.objects.get(pk=request.POST['segment'])
    variant = PageVariant(page=page, slug=request.POST['slug'], segment=segment)
    variant.save()
    version = PageVersion(variant=variant, content=content, version=1, active=True)
    version.save()
    return HttpResponseRedirect(reverse('admin.views.page_version_edit', args=[version.id]))

def page_variant_edit(request, version):
    # Not used yet, should be called from page_edit
    return HttpResponseRedirect(reverse('admin.views.page_version_edit', args=[version]))

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
        activeVersions = PageVersion.objects.filter(variant__page=version.variant.page).filter(active=True)
        versions = PageVersion.objects.filter(variant=version.variant).order_by('-version')
        segments = Segment.objects.exclude(name='default')
        context = {'page': version.variant.page, 'variant': version.variant,
          'activeVersions': activeVersions, 'versions': versions, 'version': version, 'segments': segments}
        return render(request, 'admin/page/edit_variant.html', context)
    elif(request.method == 'POST'):
        version = PageVersion.objects.get(pk=version)
        version.content.content = request.POST['content']
        version.content.save()
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

#def page_variant_swap(request, version, pri1, pri2):
#    variant1 = PageVariant.objects.filter(version=version).get(priority=pri1)
#    variant2 = PageVariant.objects.filter(version=version).get(priority=pri2)
#    variant1.priority = pri2
#    variant2.priority = pri1
#    variant1.save()
#    variant2.save()
#    return HttpResponseRedirect(reverse('admin.views.page_version_edit', args=[version]))

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
