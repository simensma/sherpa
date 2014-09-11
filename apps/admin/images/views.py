from cStringIO import StringIO
from datetime import datetime
from hashlib import sha1
import json
import logging
import sys
import zipfile

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings

import PIL.Image
import boto
import pyexiv2

from core.models import Tag
from admin.models import Image, Album, Fotokonkurranse
from user.models import User
from core import xmp
from core.util import s3_bucket
from admin.images.util import parse_objects, list_parents, list_parents_values, full_archive_search, get_exif_tags, create_thumb, generate_unique_random_image_key

logger = logging.getLogger('sherpa')

# Note: A lot of views includes 'origin', used for redirects after posting (e.g. when moving images)
# because we want to redirect to the page where the action was taken.
# Consider using a session variable instead, including hidden form field is kind of inconvenient

def index(request):
    return redirect('admin.images.views.user_images', request.user.id)

def user_images(request, user):
    user = User.get_users().get(id=user)
    images = Image.objects.filter(uploader=user)
    if user == request.user:
        current_navigation = 'personal'
    else:
        current_navigation = ''

    context = {
        'active_user': user,
        'images': images,
        'origin': request.get_full_path(),
        'all_users': sorted(User.sherpa_users(), key=lambda u: u.get_first_name()),
        'current_navigation': current_navigation,
        'image_search_length': settings.IMAGE_SEARCH_LENGTH
    }
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

    fotokonkurranse_album = Fotokonkurranse.objects.get().album
    context = {
        'album': album,
        'albums': albums,
        'albumpath': parents,
        'current_album': current_album,
        'images': images,
        'origin': request.get_full_path(),
        'all_users': sorted(User.sherpa_users(), key=lambda u: u.get_first_name()),
        'current_navigation': 'albums',
        'image_search_length': settings.IMAGE_SEARCH_LENGTH,
        'fotokonkurranse_album': fotokonkurranse_album,
    }
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
        'origin': request.get_full_path(),
        'all_users': sorted(User.sherpa_users(), key=lambda u: u.get_first_name()),
        'current_navigation': 'albums'
    }
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
        return redirect('admin.images.views.list_albums', destination_album.id)
    elif request.POST.get('origin', '') != '':
        return redirect(request.POST['origin'])
    else:
        return redirect('admin.images.views.list_albums')

def delete_items(request, album):
    Album.objects.filter(id__in=json.loads(request.POST['albums'])).delete()
    Image.objects.filter(id__in=json.loads(request.POST['images'])).delete()
    if request.POST.get('origin', '') != '':
        return redirect(request.POST['origin'])
    elif album is None:
        return redirect('admin.images.views.list_albums')
    else:
        album = Album.objects.get(id=album)
        return redirect('admin.images.views.list_albums', album.id)

def add_album(request, parent):
    parent = None if parent is None else Album.objects.get(id=parent)
    album = Album(name=request.POST['name'], parent=parent)
    album.save()
    if parent is None:
        return redirect('admin.images.views.list_albums')
    else:
        return redirect('admin.images.views.list_albums', parent.id)

def update_album(request):
    albums = Album.objects.filter(id__in=json.loads(request.POST['albums']))
    for album in albums:
        album.name = request.POST['name']
        album.save()
    parent = albums[0].parent
    if parent is None:
        return redirect('admin.images.views.list_albums')
    else:
        return redirect('admin.images.views.list_albums', parent.id)

def download_album(request, album):
    album = Album.objects.get(id=album)

    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(s3_bucket())

    def set_exif_tag(metadata, key, value):
        if key in metadata:
            metadata[key].value = value
        else:
            metadata[key] = pyexiv2.ExifTag(key, value)

    def download_image_with_retry(image, memory_file, memory_file_index, zip_archive, file_count):
        image_key = bucket.get_key("%s%s.%s" % (settings.AWS_IMAGEGALLERY_PREFIX, image.key, image.extension))
        image_data = image_key.get_contents_as_string()

        # Write relevant exif data
        metadata = pyexiv2.ImageMetadata.from_buffer(image_data)
        metadata.read()
        set_exif_tag(metadata, 'Exif.Image.ImageDescription', image.description)
        set_exif_tag(metadata, 'Exif.Image.Artist', image.photographer)
        set_exif_tag(metadata, 'Exif.Image.Copyright', image.licence)
        metadata.write()

        # And add the modified image to the zip archive
        if image.photographer == '':
            image_filename = '%s-%s.%s' % (album.name, file_count, image.extension)
        else:
            image_filename = '%s-%s-%s.%s' % (album.name, file_count, image.photographer, image.extension)
        zip_archive.writestr(image_filename.encode('ascii', 'ignore'), metadata.buffer)

        # Rewind the memory file back, read the written data, and yield it to our response,
        # while we'll go fetch the next file from S3
        next_memory_file_index = memory_file.tell()
        memory_file.seek(memory_file_index)
        return next_memory_file_index, memory_file.read()

    def build_zipfile():
        memory_file = StringIO()
        zip_archive = zipfile.ZipFile(memory_file, 'w')
        memory_file_index = 0 # Used to keep track of the amount of written data each iteration

        for file_count, image in enumerate(Image.objects.filter(album=album), start=1):
            memory_file_index, data = download_image_with_retry(image, memory_file, memory_file_index, zip_archive, file_count)
            yield data

        # Now close the archive and yield the final piece of data written
        zip_archive.close()
        memory_file.seek(memory_file_index)
        yield memory_file.read()

    response = HttpResponse(build_zipfile(), content_type='application/x-zip-compressed')
    response['Content-Disposition'] = 'attachment; filename="%s.zip"' % album.name.encode('utf-8')
    return response

def update_images(request):
    if request.method == 'GET':
        ids = json.loads(request.GET['bilder'])
        context = {
            'ids': json.dumps(ids),
            'origin': request.GET.get('origin', '')
        }
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
                return redirect(request.GET['origin'])
            else:
                return redirect('admin.images.views.list_albums')
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
            return redirect('admin.images.views.list_albums', request.POST['album'])
        elif request.POST.get('origin', '') != '':
            return redirect(request.POST['origin'])
        else:
            return redirect('admin.images.views.list_albums')

def upload_image(request):
    try:
        if len(request.FILES.getlist('files')) == 0:
            result = json.dumps({'status': 'no_files'})
            return render(request, 'common/admin/images/iframe.html', {'result': result})

        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        bucket = conn.get_bucket(s3_bucket())

        ids = []
        album = None if request.POST['album'] == '' else Album.objects.get(id=request.POST['album'])
        for image in request.FILES.getlist('files'):
            image_key = generate_unique_random_image_key()
            data = image.read()
            ext = image.name.split(".")[-1].lower()
            pil_image = PIL.Image.open(StringIO(data))
            exif_json = json.dumps(get_exif_tags(pil_image))
            tags = xmp.find_keywords(data)
            thumbs = [{'size': size, 'data': create_thumb(pil_image, ext, size)} for size in settings.THUMB_SIZES]

            key = bucket.new_key("%s%s.%s" % (settings.AWS_IMAGEGALLERY_PREFIX, image_key, ext))
            key.content_type = image.content_type
            key.set_contents_from_string(data, policy='public-read')

            for thumb in thumbs:
                key = bucket.new_key("%s%s-%s.%s" % (settings.AWS_IMAGEGALLERY_PREFIX, image_key, thumb['size'], ext))
                key.content_type = image.content_type
                key.set_contents_from_string(thumb['data'], policy='public-read')

            image = Image(
                key=image_key,
                extension=ext,
                hash=sha1(data).hexdigest(),
                description='',
                album=album,
                photographer='',
                credits='',
                licence='',
                exif=exif_json,
                uploader=request.user,
                width=pil_image.size[0],
                height=pil_image.size[1])
            image.save()

            for tag in [tag.lower() for tag in tags]:
                obj, created = Tag.objects.get_or_create(name=tag)
                image.tags.add(obj)

            ids.append(image.id)
        result = json.dumps({
            'status': 'success',
            'ids': ids
        })
        return render(request, 'common/admin/images/iframe.html', {'result': result})
    except(IOError, KeyError):
        logger.warning(u"Kunne ikke parse opplastet bilde, antar at det er ugyldig bildefil",
            exc_info=sys.exc_info(),
            extra={'request': request}
        )
        result = json.dumps({'status': 'parse_error'})
        return render(request, 'common/admin/images/iframe.html', {'result': result})
    except Exception:
        logger.error(u"Ukjent exception ved bildeopplasting",
            exc_info=sys.exc_info(),
            extra={'request': request}
        )
        result = json.dumps({'status': 'unknown_exception'})
        return render(request, 'common/admin/images/iframe.html', {'result': result})

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
        'all_users': sorted(User.sherpa_users(), key=lambda u: u.get_first_name())
    }
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
        'search_query': request.GET['q']})
    return render(request, 'common/admin/images/search.html', context)

def photographer(request):
    images = Image.objects.all()
    for word in request.GET['q'].split():
        images = images.filter(photographer__icontains=word)
    images = images.distinct('photographer')
    photographers = [image.photographer for image in images]
    return HttpResponse(json.dumps(photographers))

def set_fotokonkurranse_album(request, new_album):
    fotokonk = Fotokonkurranse.objects.get()
    if new_album is None:
        prev_album = fotokonk.album
        fotokonk.album = None
        fotokonk.save()
        return redirect('admin.images.views.list_albums', prev_album.id)
    else:
        fotokonk.album = Album.objects.get(id=new_album)
        fotokonk.save()
        return redirect('admin.images.views.list_albums', new_album)
