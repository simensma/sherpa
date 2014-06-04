from django.shortcuts import render

from core.models import Site

def index(request, site):
    active_site = Site.objects.get(id=site)

    # Generate a list of children-foreninger with site to display
    children_foreninger_with_site = []
    for forening in request.active_forening.get_children_deep():
        # Verify that the forening has at least one site
        if forening.sites.count() == 0:
            continue

        # Check that the user has admin-access to the forening
        # This would be mighty slow if user.all_foreninger wasn't cached
        for user_forening in request.user.all_foreninger():
            if forening == user_forening and user_forening.role == 'admin':
                children_foreninger_with_site.append(forening)

    context = {
        'active_site': active_site,
        'children_foreninger_with_site': children_foreninger_with_site,
    }
    return render(request, 'common/admin/sites/index.html', context)
