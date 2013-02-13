from django.shortcuts import render

from sherpa2.models import Condition


def index(request):
    conditions = Condition.get_ordered_recent()
    context = {
        'conditions': conditions}
    return render(request, 'main/conditions/index.html', context)
