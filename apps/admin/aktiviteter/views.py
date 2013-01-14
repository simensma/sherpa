from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from aktiviteter.models import Aktivitet

from datetime import datetime

def index(request):
    aktiviteter = Aktivitet.objects.all().order_by('-start_date')
    context = {'aktiviteter': aktiviteter}
    return render(request, 'common/admin/aktiviteter/index.html', context)

def new(request):
    aktivitet = Aktivitet(start_date=datetime.now())
    aktivitet.save()
    return HttpResponseRedirect(reverse('admin.aktiviteter.views.edit', args=[aktivitet.id]))

def edit(request, aktivitet):
    aktivitet = Aktivitet.objects.get(id=aktivitet)
    context = {'aktivitet': aktivitet}
    return render(request, 'common/admin/aktiviteter/edit.html', context)
