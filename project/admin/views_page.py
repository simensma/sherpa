from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from page.models import Page
from page.models import PageContent
from page.models import PageVersion
from analytics.models import PageVariant

def page_list(request, error=None):
    actives = PageVersion.objects.filter(active=True)
    context = {'actives': actives, 'error': error}
    return render(request, 'admin/page/list.html', context)

def page_new(request):
    page = Page(slug=request.POST['slug'], published=False)
    page.save()
    content = PageContent(content="Ny artikkel")
    content.save()
    version = PageVersion(page=page, content=content, version="1", active=True)
    version.save()
    return HttpResponseRedirect(reverse('admin.views.page_edit', args=[page.id, version.id]))

def page_edit(request, page, version):
    # todo: handle errors
    page = Page.objects.get(id=page)
    page.slug = request.POST['slug']
    page.save()
    return HttpResponseRedirect(reverse('admin.views.page_version_edit', args=[page.id, version]))

def page_delete(request, page):
    try:
        page = Page.objects.get(pk=page)
        versions = PageVersion.objects.filter(page=page)
        for version in versions:
            variants = PageVariant.objects.filter(version=version)
            for variant in variants:
                variant.content.delete()
            version.content.delete()
            variants.delete()
        # versions will be deleted by page cascade
        page.delete()
        return HttpResponseRedirect(reverse('admin.views.page_list'))
    except (KeyError, Page.DoesNotExist):
        return page_list(request, error="The page you tried to delete does not exist.")
