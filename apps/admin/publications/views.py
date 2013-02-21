from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from admin.models import Publication

def index(request):
    context = {}
    return render(request, 'common/admin/publications/index.html', context)

def create(request):
    publication = Publication(
        title=request.POST['title'],
        association=request.session['active_association'])
    publication.save()
    return HttpResponseRedirect(reverse('admin.publications.views.edit', args=[publication.id]))

def edit(request, publication):
    publication = Publication.objects.get(id=publication)
    context = {'publication': publication}
    return render(request, 'common/admin/publications/edit.html', context)
