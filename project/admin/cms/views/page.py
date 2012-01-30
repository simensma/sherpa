from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from project.page.models import Page, PageVariant, PageVersion
from project.analytics.models import Segment

def list(request):
    versions = PageVersion.objects.filter(variant__segment__isnull=True, active=True)
    context = {'versions': versions}
    return render(request, 'admin/cms/editor/advanced/list.html', context)

def new(request):
    page = Page(slug=request.POST['slug'], published=False)
    page.save()
    variant = PageVariant(page=page, slug='', segment=None, priority=1)
    variant.save()
    content = PageContent(content="Ny artikkel")
    content.save()
    version = PageVersion(variant=variant, content=content, version=1, active=True)
    version.save()
    return HttpResponseRedirect(reverse('admin.cms.views.variant.edit', args=[variant.id]))

def edit(request, page):
    if(request.method == 'GET'):
        page = Page.objects.get(pk=page)
        variants = PageVariant.objects.filter(page=page).order_by('priority')
        for variant in variants:
            variant.active = PageVersion.objects.get(variant=variant, active=True)
        segments = Segment.objects.exclude(name='default')
        context = {'page': page, 'variants': variants, 'segments': segments}
        return render(request, 'admin/cms/editor/advanced/edit_page.html', context)
    elif(request.method == 'POST'):
        page = Page.objects.get(pk=page)
        page.slug = request.POST['slug']
        page.save()
        return HttpResponseRedirect(reverse('admin.cms.views.page.edit', args=[page.id]))

def delete(request, page):
    return HttpResponseRedirect(reverse('admin.cms.views.page.list'))
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
#        return HttpResponseRedirect(reverse('admin.cms.views.page.list'))
#    except (KeyError, Page.DoesNotExist):
#        return page_list(request, error="The page you tried to delete does not exist.")
