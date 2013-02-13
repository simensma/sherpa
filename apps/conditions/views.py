from django.shortcuts import render

from sherpa2.models import Condition


def index(request):
    conditions = Condition.get_all().order_by('-date_observed')[:10]
    context = {
        'conditions': conditions}
    return render(request, 'main/conditions/index.html', context)
