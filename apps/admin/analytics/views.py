from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.cache import cache

from core.models import Search

@login_required
def index(request):
    return render(request, 'admin/analytics/index.html')

@login_required
def searches(request):
    most_searched = cache.get('analytics.searches.most_searched')
    if most_searched == None:
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
    return render(request, 'admin/analytics/searches.html', context)