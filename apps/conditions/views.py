from django.shortcuts import render
from django.core.cache import cache

from sherpa2.models import Condition

def index(request):
    conditions = cache.get('conditions.recent')
    if conditions is None:
        conditions = Condition.get_ordered_recent()
        cache.set('conditions.recent', conditions, 60 * 10)
    available_locations = set()
    for condition in conditions:
        available_locations.update(condition.get_locations())
    available_locations = sorted(available_locations, key=lambda l: l.name)
    context = {
        'conditions': conditions,
        'available_locations': available_locations,
    }
    return render(request, 'central/conditions/index.html', context)
