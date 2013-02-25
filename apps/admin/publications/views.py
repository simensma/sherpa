from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages

from association.models import Association
from admin.models import Publication, Release
from core.models import Tag

from datetime import datetime
import json

def index(request):
    publications = Publication.objects.all().order_by('title')
    context = {'publications': publications}
    return render(request, 'common/admin/publications/index.html', context)

def create_publication(request):
    publication = Publication(
        title=request.POST['title'],
        association=request.session['active_association'])
    publication.save()
    return HttpResponseRedirect(reverse('admin.publications.views.edit_publication', args=[publication.id]))

def edit_publication(request, publication):
    publication = Publication.objects.get(id=publication)
    if request.method == 'GET':
        context = {'publication': publication}
        return render(request, 'common/admin/publications/edit_publication.html', context)
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
        return HttpResponseRedirect(reverse('admin.publications.views.edit_publication', args=[publication.id]))

def edit_release(request, publication, release):
    if request.method == 'GET':
        publication = Publication.objects.get(id=publication)
        release = Release.objects.get(id=release) if release is not None else None
        context = {
            'publication': publication,
            'release': release,
            'now': datetime.now()}
        return render(request, 'common/admin/publications/edit_release.html', context)
    elif request.method == 'POST':
        publication = Publication.objects.get(id=publication)
        if release is None:
            release = Release(publication=publication)
        else:
            release = Release.objects.get(id=release)
        release.title = request.POST['title']
        release.cover_photo = request.POST['cover_photo']
        release.description = request.POST['description']
        release.pub_date = datetime.strptime(request.POST['pub_date'], "%d.%m.%Y")
        release.save()
        release.tags.clear()
        for tag in [tag.lower() for tag in json.loads(request.POST['tags-serialized'])]:
            obj, created = Tag.objects.get_or_create(name=tag)
            release.tags.add(obj)
        return HttpResponseRedirect(reverse('admin.publications.views.edit_publication', args=[publication.id]))
