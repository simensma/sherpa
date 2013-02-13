from django.shortcuts import render

from sherpa2.models import Condition


def index(request):
    conditions = Condition.get_ordered_recent()
    available_locations = set()
    for condition in conditions:
        available_locations.update(condition.get_locations())
    available_locations = sorted(available_locations, key=lambda l: l.name)
    context = {
        'conditions': conditions,
        'available_locations': available_locations}
    return render(request, 'main/conditions/index.html', context)
