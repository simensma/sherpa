from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from project.page.models import Menu, Page, Variant, Version
from project.analytics.models import Segment

@login_required
def list(request):
    pages = Page.objects.all()
    menus = Menu.objects.all().order_by('order')
    context = {'pages': pages, 'menus': menus, 'site': request.site}
    return render(request, 'admin/pages/list.html', context)

@login_required
def new(request):
    page = Page(title=request.POST['title'], slug=request.POST['slug'], published=False, publisher=request.user.get_profile())
    page.save()
    variant = Variant(page=page, article=None, name='Standard', segment=None, priority=1, publisher=request.user.get_profile())
    variant.save()
    version = Version(variant=variant, version=1, publisher=request.user.get_profile(), active=True)
    version.save()
    return HttpResponseRedirect(reverse('admin.cms.views.version.edit', args=[version.id]))

@login_required
def edit(request, page):
    page = Page.objects.get(id=page)
    version = Version.objects.get(variant__page=page, active=True)
    context = {'page': page, 'version': version, 'site': request.site}
    return render(request, 'admin/pages/edit.html', context)

@login_required
def delete(request, page):
    Page.objects.get(id=page).delete()
    return HttpResponseRedirect(reverse('admin.cms.views.page.list'))
