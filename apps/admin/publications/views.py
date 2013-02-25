from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages

from association.models import Association
from admin.models import Publication

def index(request):
    publications = Publication.objects.all().order_by('title')
    context = {'publications': publications}
    return render(request, 'common/admin/publications/index.html', context)

def create(request):
    publication = Publication(
        title=request.POST['title'],
        association=request.session['active_association'])
    publication.save()
    return HttpResponseRedirect(reverse('admin.publications.views.edit', args=[publication.id]))

def edit(request, publication):
    publication = Publication.objects.get(id=publication)
    if request.method == 'GET':
        context = {'publication': publication}
        return render(request, 'common/admin/publications/edit.html', context)
    elif request.method == 'POST':
        publication.title = request.POST['title']
        association = Association.objects.get(id=request.POST['association'])
        if association in request.user.get_profile().all_associations():
            publication.association = association
        if request.POST['license'] in [l[0] for l in Publication.LICENSE_CHOICES]:
            publication.license = request.POST['license']
        publication.logo = request.POST['logo']
        publication.save()
        messages.info(request, 'publication_info_saved')
        return HttpResponseRedirect(reverse('admin.publications.views.edit', args=[publication.id]))
