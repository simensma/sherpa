from django.shortcuts import render, redirect
from django.core.cache import cache
from django.conf import settings

from analytics.models import Search, NotFound
from core.models import Site

def index(request, site):
    active_site = Site.objects.get(id=site)
    context = {
        'active_site': active_site,
        'ga_account_username': settings.GA_ACCOUNT_USERNAME,
        'ga_account_password': settings.GA_ACCOUNT_PASSWORD,
    }
    return render(request, 'common/admin/sites/settings/analytics/index.html', context)

def analytics_ua(request, site):
    active_site = Site.objects.get(id=site)
    ua = request.POST['analytics-ua'].strip()
    if ua == '':
        ua = None
    active_site.analytics_ua = ua
    active_site.save()
    return redirect('admin.sites.settings.analytics.views.index', active_site.id)

def searches(request, site):
    active_site = Site.objects.get(id=site)
    most_searched = cache.get('analytics.searches.most_searched')
    if most_searched is None:
        searches = Search.on(active_site).all()
        hashes = {}

        for search in searches:
            hashes[search.query.lower()] = hashes.get(search.query.lower(), 0) + 1

        most_searched = []
        for query, count in hashes.items():
            most_searched.append({'query': query, 'count': count})

        most_searched = sorted(most_searched, key=lambda search: -search['count'])
        cache.set('analytics.searches.most_searched', most_searched, 60 * 60 * 24)

    latest_searches = Search.on(active_site).all().order_by('-date')[:50]

    context = {
        'active_site': active_site,
        'most_searched': most_searched,
        'latest_searches': latest_searches,
    }
    return render(request, 'common/admin/sites/settings/analytics/searches.html', context)

def not_found(request, site):
    active_site = Site.objects.get(id=site)
    most_requested = cache.get('analytics.not_found.most_requested')
    if most_requested is None:
        hits = NotFound.on(active_site).all()
        hashes = {}

        for hit in hits:
            hashes[hit.path.lower()] = hashes.get(hit.path.lower(), 0) + 1

        most_requested = []
        for path, count in hashes.items():
            most_requested.append({'path': path, 'count': count})

        most_requested = sorted(most_requested, key=lambda search: -search['count'])
        cache.set('analytics.not_found.most_requested', most_requested, 60 * 60 * 24)

    latest_requests = NotFound.on(active_site).all().order_by('-date')[:50]

    context = {
        'active_site': active_site,
        'most_requested': most_requested,
        'latest_requests': latest_requests,
    }
    return render(request, 'common/admin/sites/settings/analytics/not_found.html', context)
