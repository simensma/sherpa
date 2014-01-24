from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.core.cache import cache
from django.conf import settings
from django.contrib import messages

from foreninger.models import Forening
from admin.models import Publication, Release
from core.models import Tag

from datetime import datetime
import json
import hashlib
import simples3

def index(request):
    publications = Publication.objects.filter(forening__in=request.user.all_foreninger()).order_by('title')
    context = {
        'publications': publications,
        'forening_main_mappings': json.dumps(get_forening_main_mappings())
    }
    return render(request, 'common/admin/publications/index.html', context)

def edit_publication(request, publication):
    if publication is None:
        publication = Publication(forening=request.session['active_forening'])
    else:
        publication = Publication.objects.get(id=publication)

    if publication.forening not in request.user.all_foreninger():
        raise PermissionDenied

    if request.method == 'GET':
        context = {
            'publication': publication,
            'forening_main_mappings': json.dumps(get_forening_main_mappings()),
            'now': datetime.now()
        }
        return render(request, 'common/admin/publications/edit_publication.html', context)
    elif request.method == 'POST':
        publication.title = request.POST['title']
        publication.description = request.POST['description']
        if publication.title == '':
            publication.title = '(Uten navn)'
        forening = Forening.objects.get(id=request.POST['forening'])
        if forening in request.user.all_foreninger():
            publication.forening = forening
        if 'access' in request.POST and request.POST['access'] in [l[0] for l in Publication.ACCESS_CHOICES]:
                publication.access = request.POST['access']
        if 'license' in request.POST and request.POST['license'] in [l[0] for l in Publication.LICENSE_CHOICES]:
                publication.license = request.POST['license']
        publication.save()
        messages.info(request, 'publication_info_saved')
        return redirect('admin.publications.views.edit_publication', publication.id)

def edit_release(request, publication, release):
    publication = Publication.objects.get(id=publication)
    if publication.forening not in request.user.all_foreninger():
        raise PermissionDenied

    if request.method == 'GET':
        release = Release.objects.get(id=release)
        context = {
            'publication': publication,
            'release': release,
            'now': datetime.now()
        }
        return render(request, 'common/admin/publications/edit_release.html', context)
    elif request.method == 'POST':
        if release is None:
            release = Release(publication=publication)
        else:
            release = Release.objects.get(id=release)

        release.title = request.POST['title']
        if release.title == '':
            release.title = '(Uten navn)'
        release.cover_photo = request.POST['cover_photo']
        release.description = request.POST['description']
        release.online_view = request.POST['online_view'] if request.POST['online_view'] != 'http://' else ''
        release.pub_date = datetime.strptime(request.POST['pub_date'], "%d.%m.%Y")

        if 'pdf' in request.FILES:
            file = request.FILES['pdf']

            # TODO: Consider streaming the file instead of reading everything into memory first.
            # See simples3/htstream.py
            data = file.read()

            # Calculate the sha1-hash and file extension
            sha1 = hashlib.sha1()
            sha1.update(data)
            hash = sha1.hexdigest()
            extension = file.name.split(".")[-1].lower()

            # Require PDF-format.
            # Note: If you change this, you'll have to store the extension in the model,
            # as it's currently assumed to be pdf.
            if file.content_type != 'application/pdf' or extension != 'pdf':
                messages.error(request, 'incorrect_file_format')
                if release.id is None:
                    return redirect('admin.publications.views.edit_publication', publication.id)
                else:
                    return redirect('admin.publications.views.edit_publication', publication.id, release.id)

            # Upload to AWS
            s3 = simples3.S3Bucket(
                settings.AWS_BUCKET,
                settings.AWS_ACCESS_KEY_ID,
                settings.AWS_SECRET_ACCESS_KEY,
                'https://%s' % settings.AWS_BUCKET)

            if release.pdf_hash != '':
                s3.delete("%s/%s.pdf" % (settings.AWS_PUBLICATIONS_PREFIX, release.pdf_hash))

            s3.put(
                "%s/%s.%s" % (settings.AWS_PUBLICATIONS_PREFIX, hash, extension),
                data,
                acl='public-read',
                mimetype=file.content_type)
            release.pdf_hash = hash
            release.pdf_file_size = file.size

        release.save()

        release.tags.clear()
        for tag in [tag.lower() for tag in json.loads(request.POST['tags-serialized'])]:
            obj, created = Tag.objects.get_or_create(name=tag)
            release.tags.add(obj)
        return redirect('admin.publications.views.edit_publication', publication.id)

def delete_release(request, release):
    release = Release.objects.get(id=release)
    if release.publication.forening not in request.user.all_foreninger():
        raise PermissionDenied

    release.delete()
    return redirect('admin.publications.views.edit_publication', release.publication.id)

def delete_publication(request, publication):
    publication = Publication.objects.get(id=publication)
    if publication.forening not in request.user.all_foreninger():
        raise PermissionDenied

    publication.delete()
    return redirect('admin.publications.views.index')

def get_forening_main_mappings():
    forening_main_mappings = cache.get('forening_main_mappings')
    if forening_main_mappings is None:
        forening_main_mappings = {a.id: a.get_main_forening().name for a in Forening.objects.all()}
        cache.set('forening_main_mappings', forening_main_mappings, 60 * 60 * 24)
    return forening_main_mappings
