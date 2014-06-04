from django.shortcuts import render

from core.models import Site

def index(request, site):
    active_site = Site.objects.get(id=site)
    context = {
        'active_site': active_site,
    }
    return render(request, 'common/admin/sites/settings/index.html', context)
