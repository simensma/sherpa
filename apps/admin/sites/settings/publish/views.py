from django.shortcuts import render, redirect

from core.models import Site

def index(request, site):
    active_site = Site.objects.get(id=site)
    context = {'active_site': active_site}
    return render(request, 'common/admin/sites/settings/publish/index.html', context)

def publish(request, site):
    active_site = Site.objects.get(id=site)
    active_site.is_published = True
    active_site.save()
    return redirect('admin.sites.settings.publish.views.index', active_site.id)

def unpublish(request, site):
    active_site = Site.objects.get(id=site)
    active_site.is_published = False
    active_site.save()
    return redirect('admin.sites.settings.publish.views.index', active_site.id)
