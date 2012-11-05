from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.cache import cache

from core.models import Search

def index(request):
    return render(request, 'main/admin/analytics/index.html')

def searches(request):
    most_searched = cache.get('analytics.searches.most_searched')
    if most_searched is None:
        searches = Search.objects.all()
        hashes = {}

        for search in searches:
            hashes[search.query.lower()] = hashes.get(search.query.lower(), 0) + 1

        most_searched = []
        for query, count in hashes.items():
            most_searched.append({'query': query, 'count': count})

        most_searched = sorted(most_searched, key=lambda search: -search['count'])
        cache.set('analytics.searches.most_searched', most_searched, 60 * 60 * 24)

    latest_searches = Search.objects.all().order_by('-date')[:50]

    context = {'most_searched': most_searched, 'latest_searches': latest_searches}
    return render(request, 'main/admin/analytics/searches.html', context)
