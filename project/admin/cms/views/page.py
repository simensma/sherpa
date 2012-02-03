from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from project.page.models import Menu, Page, PageVariant, PageVersion
from project.analytics.models import Segment

def list(request):
    versions = PageVersion.objects.filter(variant__segment__isnull=True, active=True)
    menus = Menu.objects.all().order_by('order')
    context = {'versions': versions, 'menus': menus}
    return render(request, 'admin/cms/pages.html', context)

def new(request):
    page = Page(title=request.POST['title'], slug=request.POST['slug'], published=False)
    page.save()
    variant = PageVariant(page=page, name='Standard', slug='', segment=None, priority=1)
    variant.save()
    version = PageVersion(variant=variant, version=1, active=True)
    version.save()
    return HttpResponseRedirect(reverse('admin.cms.views.page.list'))

def edit(request, page):
    if(request.method == 'GET'):
        page = Page.objects.get(pk=page)
        variants = PageVariant.objects.filter(page=page).order_by('priority')
        for variant in variants:
            variant.active = PageVersion.objects.get(variant=variant, active=True)
        segments = Segment.objects.exclude(name='default')
        context = {'page': page, 'variants': variants, 'segments': segments}
        return render(request, 'admin/cms/edit_page.html', context)
    elif(request.method == 'POST'):
        page = Page.objects.get(pk=page)
        page.slug = request.POST['slug']
        page.save()
        return HttpResponseRedirect(reverse('admin.cms.views.page.edit', args=[page.id]))

def delete(request, page):
    page = Page.objects.get(id=page)
    page.deep_delete()
    return HttpResponseRedirect(reverse('admin.cms.views.page.list'))
