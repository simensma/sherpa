from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from page.models import Page, PageVariant, PageVersion, PageContent
from analytics.models import Segment

def page_list(request):
    versions = PageVersion.objects.filter(variant__segment__isnull=True, active=True)
    context = {'versions': versions}
    return render(request, 'admin/page/list.html', context)

def page_new(request):
    page = Page(slug=request.POST['slug'], published=False)
    page.save()
    variant = PageVariant(page=page, slug=None, segment=None)
    variant.save()
    content = PageContent(content="Ny artikkel")
    content.save()
    version = PageVersion(variant=variant, content=content, version=1, active=True)
    version.save()
    return HttpResponseRedirect(reverse('admin.views.page_variant_edit', args=[variant.id]))

def page_edit(request, page):
    if(request.method == 'GET'):
        page = Page.objects.get(pk=page)
        activeVersions = PageVersion.objects.filter(variant__page=page, active=True)
        variants = PageVariant.objects.filter(page=page)
        for variant in variants:
            variant.active = PageVersion.objects.get(variant=variant, active=True)
        segments = Segment.objects.exclude(name='default')
        context = {'page': page, 'variants': variants, 'activeVersions': activeVersions, 'segments': segments}
        return render(request, 'admin/page/edit_page.html', context)
    elif(request.method == 'POST'):
        page = Page.objects.get(pk=page)
        page.slug = request.POST['slug']
        page.save()
        return HttpResponseRedirect(reverse('admin.views.page_edit', args=[page.id]))

def page_delete(request, page):
    return HttpResponseRedirect(reverse('admin.views.page_list'))
#    try:
#        page = Page.objects.get(pk=page)
#        versions = PageVersion.objects.filter(page=page)
#        for version in versions:
#            variants = PageVariant.objects.filter(version=version)
#            for variant in variants:
#                variant.content.delete()
#            version.content.delete()
#            variants.delete()
#        # versions will be deleted by page cascade
#        page.delete()
#        return HttpResponseRedirect(reverse('admin.views.page_list'))
#    except (KeyError, Page.DoesNotExist):
#        return page_list(request, error="The page you tried to delete does not exist.")
