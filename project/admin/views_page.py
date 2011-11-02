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
    page = Page(slug=request.POST['slug'])
    page.save()
    content = PageContent(content=request.POST['content'])
    content.save()
    version = PageVersion(page=page, content=content, version="1", active=True)
    version.save()
    return HttpResponseRedirect(reverse('admin.views.page_edit', args=[page.id, version.id]))

def page_edit(request, page, version):
    if(request.method == 'GET'):
        try:
            versions = PageVersion.objects.filter(page=page)
            version = versions.get(pk=version)
            active = versions.get(active=True)
            context = {'version': version, 'active': active}
            return render(request, 'admin/page/edit_page.html', context)
        except (KeyError, Page.DoesNotExist):
            return page_list(request, error="This page does not exist.")
    elif(request.method == 'POST'):
        try:
            page = Page.objects.get(id=page)
            page.slug = request.POST['slug']
            page.save()
            version = PageVersion.objects.filter(page=page).get(id=version)
            content = PageContent.objects.get(pageversion=version)
            content.content = request.POST['content']
            content.save()
            return HttpResponseRedirect(reverse('admin.views.page_edit', args=[page.id, version.id]))
        except (KeyError, Page.DoesNotExist):
            content = PageContent(version=1.0, content=request.POST['content'])
            page = Page(active=content, slug=request.POST['slug'])
            context = {'page': page, 'error': "Whoops, looks like you tried to edit a non-existing thing."}
            return render(request, 'admin/page/edit_page.html', context)

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
