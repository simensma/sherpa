# encoding: utf-8
from django.http import HttpResponse
from django.conf import settings
from django.db.models import Q
from django.template import RequestContext
from django.template.loader import render_to_string
from django.shortcuts import render

import json

from core.models import Tag
from admin.models import Image, Album
from core import xmp

from PIL.ExifTags import TAGS
import random
from PIL import Image as pil
from cStringIO import StringIO
from hashlib import sha1
import simples3
import logging
import sys

logger = logging.getLogger('sherpa')

def content_dialog(request):
    album = json.loads(request.POST['album'])
    if album == '':
        objects = parse_objects([], Album.objects.filter(parent=None).order_by('name'), [])
    else:
        current_album = Album.objects.get(id=album)
        objects = parse_objects(list_parents(current_album),
            Album.objects.filter(parent=album).order_by('name'),
            Image.objects.filter(album=album))

    context = RequestContext(request, {
        'parents': objects['parents'],
        'albums': objects['albums'],
        'albums_divided': divide_for_three_columns(objects['albums']),
        'images': objects['images'],
        'list_status': 'album' if album != '' else 'root_album'
        })
    return HttpResponse(json.dumps({'html': render_to_string('common/admin/images/util/image-archive-picker-content.html', context)}))

def mine_dialog(request):
    images = Image.objects.filter(uploader=request.user)

    context = RequestContext(request, {
        'images': images,
        'list_status': 'album'
        })
    return HttpResponse(json.dumps({'html': render_to_string('common/admin/images/util/image-archive-picker-content.html', context)}))

def search_dialog(request):
    query = json.loads(request.POST['query'])
    if len(query) < settings.IMAGE_SEARCH_LENGTH:
        albums = Album.objects.none()
        images = Image.objects.none()
    else:
        albums, images = full_archive_search(query)
    objects = parse_objects([], albums, images)
    context = RequestContext(request, {
        'parents': objects['parents'],
        'albums': objects['albums'],
        'albums_divided': divide_for_three_columns(objects['albums']),
        'images': objects['images'],
        'list_status': 'search',
        'search_query': query
        })
    return HttpResponse(json.dumps({'html': render_to_string('common/admin/images/util/image-archive-picker-content.html', context)}))

def image_upload_dialog(request):
    try:
        image = request.FILES['file']
    except KeyError:
        result = json.dumps({'status': 'no_files'})
        return render(request, 'common/admin/images/iframe.html', {'result': result})

    try:
        s3 = simples3.S3Bucket(
            settings.AWS_BUCKET,
            settings.AWS_ACCESS_KEY_ID,
            settings.AWS_SECRET_ACCESS_KEY,
            'https://%s' % settings.AWS_BUCKET)

        key = generate_unique_random_image_key()
        data = image.read()
        ext = image.name.split(".")[-1].lower()
        pil_image = pil.open(StringIO(data))
        exif_json = json.dumps(get_exif_tags(pil_image))
        image_file_tags = xmp.find_keywords(data)
        user_provided_tags = json.loads(request.POST['tags-serialized'])
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
            description=request.POST['description'],
            album=None,
            photographer=request.POST['photographer'],
            credits=request.POST['credits'],
            licence=request.POST['licence'],
            exif=exif_json,
            uploader=request.user,
            width=pil_image.size[0],
            height=pil_image.size[1])
        image.save()

        for tag in [tag.lower() for tag in image_file_tags + user_provided_tags]:
            obj, created = Tag.objects.get_or_create(name=tag)
            image.tags.add(obj)

        result = json.dumps({
            'status': 'success',
            'url': 'http://%s/%s%s.%s' % (settings.AWS_BUCKET, settings.AWS_IMAGEGALLERY_PREFIX, key, ext)})
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


#
# Actual utilities
#

def full_archive_search(query):
    images = Image.objects.all()
    for word in query.split():
        images = images.filter(
            Q(description__icontains=word) |
            Q(album__name__icontains=word) |
            Q(photographer__icontains=word) |
            Q(credits__icontains=word) |
            Q(licence__icontains=word) |
            Q(tags__name__icontains=word))
    images = images.distinct()

    albums = Album.objects.all()
    for word in query.split():
        albums = albums.filter(name__icontains=word)
    albums = albums.distinct()

    return albums, images

# Lol, I bet there's a much easier way to do this, but whatever, this works for now.
def divide_for_three_columns(albums):
    bulk = len(albums) / 3
    rest = len(albums) % 3

    if rest > 0:
        first = bulk + 1
        rest -= 1
    else:
        first = bulk

    if rest > 0:
        second = first + bulk + 1
    else:
        second = first + bulk

    return [albums[:first], albums[first:second], albums[second:]]

def parse_objects(parents, albums, images):
    objects = {'parents': [], 'albums': [], 'images': []}
    for parent in parents:
        objects['parents'].append({'id': parent.id, 'name': parent.name})
    for album in albums:
        objects['albums'].append({'id': album.id, 'name': album.name})
    for image in images:
        objects['images'].append({'key': image.key, 'extension': image.extension,
            'width': image.width, 'height': image.height,
            'photographer': image.photographer, 'description': image.description})
    return objects


def list_parents(album):
    parents = []
    parents.append(album)
    while(album.parent is not None):
        album = Album.objects.get(id=album.parent.id)
        parents.insert(0, album)
    return parents

def list_parents_values(album):
    parents = []
    parents.append({'id': album.id, 'name': album.name})
    while(album.parent is not None):
        album = Album.objects.get(id=album.parent.id)
        parents.insert(0, {'id': album.id, 'name': album.name})
    return parents

def generate_random_image_key():
    def random_alphanumeric():
        # These "magic" numbers generate one of [a-zA-Z0-9] based on the ascii table.
        r = random.randint(0, 61)
        if  (r < 10): return chr(r + 48)
        elif(r < 36): return chr(r + 55)
        else        : return chr(r + 61)
    return "%s%s/%s%s/%s%s" % (random_alphanumeric(), random_alphanumeric(), random_alphanumeric(), random_alphanumeric(), random_alphanumeric(), random_alphanumeric())

def generate_unique_random_image_key():
    key = generate_random_image_key()
    while Image.objects.filter(key=key).exists():
        # Potential weak spot here if the amount of objects
        # were to close in on the amount of available keys.
        key = generate_random_image_key()
    return key

def get_exif_tags(pil_image):
    try:
        exif = {}
        if hasattr(pil_image, '_getexif') and pil_image._getexif() is not None:
            for tag, value in pil_image._getexif().items():
                if tag == 37500:
                    # MakerNote data, see: https://en.wikipedia.org/wiki/Exchangeable_image_file_format#MakerNote_data
                    continue
                try:
                    # No more known binary tags. Attempt to recursively encode the data:
                    json.dumps(value)
                except UnicodeDecodeError:
                    # Skip this tag, it's not a text string
                    # TODO: Should log a warning with the tag string here.
                    continue
                exif[TAGS.get(tag, tag)] = value
    except IOError:
        # Calling _getexif() on some select images raises IOError("not enough data").
        # Not sure what that means but we'll ignore exif data on those images for now.
        return {}

def create_thumb(pil_image, extension, size):
    fp = StringIO()
    img_copy = pil_image.copy()
    img_copy.thumbnail([size, size], pil.ANTIALIAS)
    img_copy.save(fp, standardize_extension(extension))
    return fp.getvalue()

def standardize_extension(extension):
    # Force lowercase
    extension = extension.lower()

    # Some image types have common extensions (like .jpg) which are not recognized by PIL
    if extension == 'jpg':
        return 'jpeg'
    elif extension == 'tif':
        return 'tiff'
    else:
        return extension
