from django.shortcuts import render

from core.models import Site

def index(request, site):
    active_site = Site.objects.get(id=site)

    children_foreninger_with_site = [f for f in request.active_forening.get_children_deep() if f.sites.count() > 0]

    context = {
        'active_site': active_site,
        'children_foreninger_with_site': children_foreninger_with_site,
    }
    return render(request, 'common/admin/sites/index.html', context)
