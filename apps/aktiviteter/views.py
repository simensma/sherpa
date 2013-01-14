from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from aktiviteter.models import Aktivitet

def index(request):
    aktiviteter = Aktivitet.objects.all().order_by('-start_date')
    context = {'aktiviteter': aktiviteter}
    return render(request, 'common/aktiviteter/index.html', context)

def show(request, aktivitet):
    aktivitet = Aktivitet.objects.get(id=aktivitet)
    context = {'aktivitet': aktivitet}
    return render(request, 'common/aktiviteter/show.html', context)
