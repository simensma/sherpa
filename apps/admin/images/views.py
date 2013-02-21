from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.conf import settings
from django.db.models import Q

from core.models import Tag
from admin.models import Image, Album
from user.models import Profile

from admin.images.util import parse_objects, list_parents, list_parents_values, parse_image, store_image

import json
import logging
import sys
from datetime import datetime

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

        #parsing
        parsed_images = []
        for file in request.FILES.getlist('files'):
            try:
                parsed_images.append(parse_image(file))
            except(IOError, KeyError):
                return render(request, 'common/admin/images/iframe.html', {'result': 'parse_error'})

        #storing
        ids = []
        album = None if request.POST['album'] == '' else Album.objects.get(id=request.POST['album'])
        for image in parsed_images:
            stored_image = store_image(image, album, request.user)
            ids.append(stored_image['id'])
        return render(request, 'common/admin/images/iframe.html', {'result': 'success', 'ids': json.dumps(ids)})
    except Exception:
        logger.error(u"Uventet exception ved bildeopplasting",
            exc_info=sys.exc_info(),
            extra={'request': request}
        )
        return render(request, 'common/admin/images/iframe.html', {'result': 'unknown_exception'})

def fast_upload(request):
    try:
        file = request.FILES['file']
    except KeyError:
        return render(request, 'common/admin/images/iframe.html', {'result': 'no_files'})

    #parse file
    try:
        parsed_image = parse_image(file)
    except(IOError, KeyError):
        return render(request, 'common/admin/images/iframe.html', {'result': 'parse_error'})

    #store stuff on s3 and in db
    stored_image = store_image(parsed_image, None, request.user)

    #add info to image
    image = Image.objects.get(id=stored_image['id'])
    tags = json.loads(request.POST['tags-serialized'])

    if request.POST['description'] != "":  image.description = request.POST['description']
    if request.POST['photographer'] != "": image.photographer = request.POST['photographer']
    if request.POST['credits'] != "":      image.credits = request.POST['credits']
    if request.POST['licence'] != "":      image.licence = request.POST['licence']
    image.save()

    for tag in [tag.lower() for tag in tags]:
        obj, created = Tag.objects.get_or_create(name=tag)
        image.tags.add(obj)

    return render(request, 'common/admin/images/iframe.html', {'result': 'success', 'url': stored_image['url'], })

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
    images = []
    for word in request.GET['q'].split():
        images.extend(Image.objects.filter(
            Q(description__icontains=word) |
            Q(album__name__icontains=word) |
            Q(photographer__icontains=word) |
            Q(credits__icontains=word) |
            Q(licence__icontains=word) |
            Q(tags__name__icontains=word)).distinct().values())
    for word in request.GET['q'].split():
        albums = Album.objects.filter(name__icontains=word).distinct()
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
