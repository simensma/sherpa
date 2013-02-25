from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.conf import settings

from core.models import Tag
from admin.models import Image, Album
from user.models import Profile

from core import xmp
from admin.images.util import parse_objects, list_parents, list_parents_values, full_archive_search, get_exif_tags, create_thumb, generate_unique_random_image_key

import Image as pil
from cStringIO import StringIO
import json
import logging
import sys
from datetime import datetime
import simples3
from hashlib import sha1

logger = logging.getLogger('sherpa')

# Note: A lot of views includes 'origin', used for redirects after posting (e.g. when moving images)
# because we want to redirect to the page where the action was taken.
# Consider using a session variable instead, including hidden form field is kind of inconvenient

def index(request):
    return HttpResponseRedirect(reverse('admin.images.views.user_images', args=[request.user.get_profile().id]))

def user_images(request, profile):
    profile = Profile.objects.get(id=profile)
    images = Image.objects.filter(uploader=profile)
    if profile == request.user.get_profile():
        current_navigation = 'personal'
    else:
        current_navigation = ''

    context = {
        'active_profile': profile,
        'images': images,
        'aws_bucket': settings.AWS_BUCKET,
        'origin': request.get_full_path(),
        'all_users': sorted(Profile.objects.all(), key=lambda p: p.get_first_name()),
        'current_navigation': current_navigation,
        'image_search_length': settings.IMAGE_SEARCH_LENGTH}
    return render(request, 'common/admin/images/user_images.html', context)

def list_albums(request, album):
    albums = Album.objects.filter(parent=album).order_by('name')
    parents = []
    images = None
    current_album = None
    if album is not None:
        current_album = Album.objects.get(id=album)
        images = Image.objects.filter(album=album)
        parents = list_parents(current_album)
    context = {
        'album': album,
        'albums': albums,
        'albumpath': parents,
        'current_album': current_album,
        'images': images,
        'aws_bucket': settings.AWS_BUCKET,
        'origin': request.get_full_path(),
        'all_users': sorted(Profile.objects.all(), key=lambda p: p.get_first_name()),
        'current_navigation': 'albums',
        'image_search_length': settings.IMAGE_SEARCH_LENGTH}
    return render(request, 'common/admin/images/list_albums.html', context)

def image_details(request, image):
    image = Image.objects.get(id=image)
    parents = [] if image.album is None else list_parents(image.album)
    exif = json.loads(image.exif)
    try:
        taken = datetime.strptime(exif['DateTime'], '%Y:%m:%d %H:%M:%S')
    except Exception:
        taken = None
    tags = image.tags.all()
    context = {
        'image': image,
        'albumpath': parents,
        'exif': exif,
        'taken': taken,
        'tags': tags,
        'aws_bucket': settings.AWS_BUCKET,
        'origin': request.get_full_path(),
        'all_users': sorted(Profile.objects.all(), key=lambda p: p.get_first_name()),
        'current_navigation': 'albums'}
    return render(request, 'common/admin/images/image_details.html', context)

def move_items(request):
    destination_album = None if request.POST['destination_album'] == '' else Album.objects.get(id=request.POST['destination_album'])
    for album in Album.objects.filter(id__in=json.loads(request.POST['albums'])):
        def parent_in_parent(destination, child):
            while destination is not None:
                if destination == child:
                    return True
                destination = destination.parent
            return False

        if parent_in_parent(destination_album, album):
            # Tried to set an album as a child of its own children, ignore
            # Giving feedback here is slightly complicated so I'll skip it for now; the user shouldn't be this silly anyway.
            # But feedback at some point would be nice, consider looking at this
            continue

        album.parent = destination_album
        album.save()

    for image in Image.objects.filter(id__in=json.loads(request.POST['images'])):
        image.album = destination_album
        image.save()

    if destination_album is not None:
        return HttpResponseRedirect(reverse('admin.images.views.list_albums', args=[destination_album.id]))
    elif request.POST.get('origin', '') != '':
        return HttpResponseRedirect(request.POST['origin'])
    else:
        return HttpResponseRedirect(reverse('admin.images.views.list_albums'))

def delete_items(request, album):
    Album.objects.filter(id__in=json.loads(request.POST['albums'])).delete()
    Image.objects.filter(id__in=json.loads(request.POST['images'])).delete()
    if request.POST.get('origin', '') != '':
        return HttpResponseRedirect(request.POST['origin'])
    elif album is None:
        return HttpResponseRedirect(reverse('admin.images.views.list_albums'))
    else:
        album = Album.objects.get(id=album)
        return HttpResponseRedirect(reverse('admin.images.views.list_albums', args=[album.id]))

def add_album(request, parent):
    parent = None if parent is None else Album.objects.get(id=parent)
    album = Album(name=request.POST['name'], parent=parent)
    album.save()
    if parent is None:
        return HttpResponseRedirect(reverse('admin.images.views.list_albums'))
    else:
        return HttpResponseRedirect(reverse('admin.images.views.list_albums', args=[parent.id]))

def update_album(request):
    albums = Album.objects.filter(id__in=json.loads(request.POST['albums']))
    for album in albums:
        album.name = request.POST['name']
        album.save()
    parent = albums[0].parent
    if parent is None:
        return HttpResponseRedirect(reverse('admin.images.views.list_albums'))
    else:
        return HttpResponseRedirect(reverse('admin.images.views.list_albums', args=[parent.id]))

def update_images(request):
    if request.method == 'GET':
        ids = json.loads(request.GET['bilder'])
        context = {
            'aws_bucket': settings.AWS_BUCKET,
            'ids': json.dumps(ids),
            'origin': request.GET.get('origin', '')}
        if len(ids) == 1:
            context.update({'image': Image.objects.get(id=ids[0])})
            return render(request, 'common/admin/images/modify_single.html', context)
        elif len(ids) > 1:
            images = Image.objects.filter(id__in=ids)
            context.update({'images': images})
            return render(request, 'common/admin/images/modify_multiple.html', context)
        else:
            # No images to edit, not sure why, just redirect them to origin or home.
            # TODO: Should maybe log an error here in case this was our fault.
            if request.GET.get('origin', '') != '':
                return HttpResponseRedirect(request.GET['origin'])
            else:
                return HttpResponseRedirect(reverse('admin.images.views.list_albums'))
    elif request.method == 'POST':
        # Figure out which fields should be updated
        if 'fields' in request.POST:
            fields = json.loads(request.POST['fields'])
            all_fields = False
        else:
            all_fields = True

        for image in Image.objects.filter(id__in=json.loads(request.POST['ids'])):
            if all_fields or fields['description']: image.description = request.POST['description']
            if all_fields or fields['photographer']: image.photographer = request.POST['photographer']
            if all_fields or fields['credits']: image.credits = request.POST['credits']
            if all_fields or fields['licence']: image.licence = request.POST['licence']

            # Temporary if; key should always exist (need to update all forms that post to this view)
            if 'album' in request.POST:
                # If empty, the user picked the root album, but it will be a ghost image (found only when searching or under user-images)
                image.album = Album.objects.get(id=request.POST['album']) if request.POST['album'] != '' else None
            image.save()

            # Save new tags, remove existing tags if specified
            if request.POST.get('replace-tags', '') == 'true':
                image.tags.clear()
            for tag in [tag.lower() for tag in json.loads(request.POST['tags-serialized'])]:
                obj, created = Tag.objects.get_or_create(name=tag)
                image.tags.add(obj)

        # Temporary 'get': album key should always exist (need to update all forms that post to this view)
        if request.POST.get('album', '') != '':
            return HttpResponseRedirect(reverse('admin.images.views.list_albums', args=[request.POST['album']]))
        elif request.POST.get('origin', '') != '':
            return HttpResponseRedirect(request.POST['origin'])
        else:
            return HttpResponseRedirect(reverse('admin.images.views.list_albums'))

def upload_image(request):
    try:
        if len(request.FILES.getlist('files')) == 0:
            return render(request, 'common/admin/images/iframe.html', {'result': 'no_files'})

        s3 = simples3.S3Bucket(
            settings.AWS_BUCKET,
            settings.AWS_ACCESS_KEY_ID,
            settings.AWS_SECRET_ACCESS_KEY,
            'https://%s' % settings.AWS_BUCKET)

        ids = []
        album = None if request.POST['album'] == '' else Album.objects.get(id=request.POST['album'])
        for image in request.FILES.getlist('files'):
            key = generate_unique_random_image_key()
            data = image.read()
            ext = image.name.split(".")[-1].lower()
            pil_image = pil.open(StringIO(data))
            exif_json = json.dumps(get_exif_tags(pil_image))
            tags = xmp.find_keywords(data)
            thumbs = [{'size': size, 'data': create_thumb(pil_image, ext, size)} for size in settings.THUMB_SIZES]

            s3.put("%s%s.%s" % (settings.AWS_IMAGEGALLERY_PREFIX, key, ext),
                data,
                acl='public-read',
                mimetype=image.content_type)
            for thumb in thumbs:
                s3.put("%s%s-%s.%s" % (settings.AWS_IMAGEGALLERY_PREFIX, key, thumb['size'], ext),
                    thumb['data'],
                    acl='public-read',
                    mimetype=image.content_type)

            image = Image(
                key=key,
                extension=ext,
                hash=sha1(data).hexdigest(),
                description='',
                album=album,
                photographer='',
                credits='',
                licence='',
                exif=exif_json,
                uploader=request.user.get_profile(),
                width=pil_image.size[0],
                height=pil_image.size[1])
            image.save()

            for tag in [tag.lower() for tag in tags]:
                obj, created = Tag.objects.get_or_create(name=tag)
                image.tags.add(obj)

            ids.append(image.id)
        return render(request, 'common/admin/images/iframe.html', {'result': 'success', 'ids': json.dumps(ids)})
    except(IOError, KeyError):
        logger.warning(u"Kunne ikke parse opplastet bilde, antar at det er ugyldig bildefil",
            exc_info=sys.exc_info(),
            extra={'request': request}
        )
        return render(request, 'common/admin/images/iframe.html', {'result': 'parse_error'})
    except Exception:
        logger.error(u"Ukjent exception ved bildeopplasting",
            exc_info=sys.exc_info(),
            extra={'request': request}
        )
        return render(request, 'common/admin/images/iframe.html', {'result': 'unknown_exception'})

def content_json(request, album):
    if album is not None:
        current_album = Album.objects.get(id=album)
        objects = parse_objects(list_parents(current_album),
            Album.objects.filter(parent=album).order_by('name'),
            Image.objects.filter(album=album))
    else:
        objects = parse_objects([], Album.objects.filter(parent=None).order_by('name'), [])
    return HttpResponse(json.dumps(objects))

def album_content_json(request, album):
    if album is not None:
        current_album = Album.objects.get(id=album)
        albums = Album.objects.filter(parent=album).order_by('name')
        path = list_parents_values(current_album)
    else:
        albums = Album.objects.filter(parent=None).order_by('name')
        path = []
    return HttpResponse(json.dumps({'albums': list(albums.values()), 'path': path}))

def album_search_json(request):
    if len(request.POST['query']) < settings.IMAGE_SEARCH_LENGTH:
        return HttpResponse('[]')

    albums = Album.objects.filter(name__icontains=request.POST['query']).order_by('name')
    items = []
    for album in albums:
        items.append(list_parents_values(album))
    return HttpResponse(json.dumps({'items': items}))

def search(request):
    context = {
        'origin': request.get_full_path(),
        'all_users': sorted(Profile.objects.all(), key=lambda p: p.get_first_name())}
    if len(request.GET.get('q', '')) < settings.IMAGE_SEARCH_LENGTH:
        context.update({
            'too_short_query': True,
            'image_search_length': settings.IMAGE_SEARCH_LENGTH,
        })
        return render(request, 'common/admin/images/search.html', context)
    albums, images = full_archive_search(request.GET['q'])
    context.update({
        'albums': albums,
        'images': images,
        'aws_bucket': settings.AWS_BUCKET,
        'search_query': request.GET['q']})
    return render(request, 'common/admin/images/search.html', context)

def photographer(request):
    images = Image.objects.filter(photographer__icontains=request.POST['name']).distinct('photographer')
    photographers = []
    for image in images:
        photographers.append(image.photographer)
    return HttpResponse(json.dumps(photographers))
