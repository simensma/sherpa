from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from project.page.models import Menu, Page, Variant, Version
from project.analytics.models import Segment

@login_required
def list(request):
    versions = Version.objects.filter(variant__page__isnull=False, variant__segment__isnull=True, active=True)
    menus = Menu.objects.all().order_by('order')
    context = {'versions': versions, 'menus': menus}
    return render(request, 'admin/cms/pages.html', context)

@login_required
def new(request):
    page = Page(title=request.POST['title'], slug=request.POST['slug'], published=False, publisher=request.user.get_profile())
    page.save()
    variant = Variant(page=page, article=None, name='Standard', slug='', segment=None, priority=1, publisher=request.user.get_profile())
    variant.save()
    version = Version(variant=variant, version=1, publisher=request.user.get_profile(), active=True)
    version.save()
    return HttpResponseRedirect(reverse('admin.cms.views.page.list'))

@login_required
def edit(request, page):
    if(request.method == 'GET'):
        page = Page.objects.get(id=page)
        variants = Variant.objects.filter(page=page).order_by('priority')
        for variant in variants:
            variant.active = Version.objects.get(variant=variant, active=True)
        segments = Segment.objects.exclude(name='default')
        context = {'page': page, 'variants': variants, 'segments': segments}
        return render(request, 'admin/cms/edit_page.html', context)
    elif(request.method == 'POST'):
        page = Page.objects.get(id=page)
        page.slug = request.POST['slug']
        page.save()
        return HttpResponseRedirect(reverse('admin.cms.views.page.edit', args=[page.id]))

@login_required
def delete(request, page):
    Page.objects.get(id=page).delete()
    return HttpResponseRedirect(reverse('admin.cms.views.page.list'))
