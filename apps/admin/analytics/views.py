from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.core.cache import cache

from analytics.models import Search, NotFound

def index(request):
    return render(request, 'common/admin/analytics/index.html')

def searches(request):
    most_searched = cache.get('analytics.searches.most_searched')
    if most_searched is None:
        searches = Search.on(request.session['active_association'].site).all()
        hashes = {}

        for search in searches:
            hashes[search.query.lower()] = hashes.get(search.query.lower(), 0) + 1

        most_searched = []
        for query, count in hashes.items():
            most_searched.append({'query': query, 'count': count})

        most_searched = sorted(most_searched, key=lambda search: -search['count'])
        cache.set('analytics.searches.most_searched', most_searched, 60 * 60 * 24)

    latest_searches = Search.on(request.session['active_association'].site).all().order_by('-date')[:50]

    context = {'most_searched': most_searched, 'latest_searches': latest_searches}
    return render(request, 'common/admin/analytics/searches.html', context)

def not_found(request):
    most_requested = cache.get('analytics.not_found.most_requested')
    if most_requested is None:
        hits = NotFound.on(request.session['active_association'].site).all()
        hashes = {}

        for hit in hits:
            hashes[hit.path.lower()] = hashes.get(hit.path.lower(), 0) + 1

        most_requested = []
        for path, count in hashes.items():
            most_requested.append({'path': path, 'count': count})

        most_requested = sorted(most_requested, key=lambda search: -search['count'])
        cache.set('analytics.not_found.most_requested', most_requested, 60 * 60 * 24)

    latest_requests = NotFound.on(request.session['active_association'].site).all().order_by('-date')[:50]

    context = {'most_requested': most_requested, 'latest_requests': latest_requests}
    return render(request, 'common/admin/analytics/not_found.html', context)
