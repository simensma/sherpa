from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from aktiviteter.models import Aktivitet
from core.models import Tag

from datetime import datetime
import json

def index(request):
    aktiviteter = Aktivitet.objects.all().order_by('-start_date')
    context = {'aktiviteter': aktiviteter}
    return render(request, 'common/admin/aktiviteter/index.html', context)

def new(request):
    aktivitet = Aktivitet(start_date=datetime.now())
    aktivitet.save()
    return HttpResponseRedirect(reverse('admin.aktiviteter.views.edit', args=[aktivitet.id]))

def edit(request, aktivitet):
    if request.method == 'GET':
        aktivitet = Aktivitet.objects.get(id=aktivitet)
        context = {'aktivitet': aktivitet}
        return render(request, 'common/admin/aktiviteter/edit.html', context)
    elif request.method == 'POST':
        # TODO: Server-side validations
        aktivitet = Aktivitet.objects.get(id=aktivitet)
        aktivitet.title = request.POST['title']
        aktivitet.description = request.POST['description']
        aktivitet.start_date = datetime.strptime("%s %s" % (request.POST['start_date'], request.POST['start_time']), "%d.%m.%Y %H:%M")
        aktivitet.tags.clear()
        aktivitet.save()
        for tag in [tag.lower() for tag in json.loads(request.POST['tags'])]:
            obj, created = Tag.objects.get_or_create(name=tag)
            aktivitet.tags.add(obj)
        return HttpResponseRedirect(reverse('admin.aktiviteter.views.edit', args=[aktivitet.id]))
