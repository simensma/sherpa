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

from PIL.ExifTags import TAGS
import random
import Image as pil
from cStringIO import StringIO
from hashlib import sha1
import simples3

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
    images = Image.objects.filter(uploader=request.user.get_profile())

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
    return random_alphanumeric() + random_alphanumeric() + '/' + random_alphanumeric() + random_alphanumeric() + '/' + random_alphanumeric() + random_alphanumeric()

def store_image(image, album, user):
    url = 'http://' + settings.AWS_BUCKET + '/' + settings.AWS_IMAGEGALLERY_PREFIX + image['key'] + '.' + image['ext']

    s3 = simples3.S3Bucket(settings.AWS_BUCKET, settings.AWS_ACCESS_KEY_ID,
        settings.AWS_SECRET_ACCESS_KEY, 'https://%s' % settings.AWS_BUCKET)
    s3.put("%s%s.%s" % (settings.AWS_IMAGEGALLERY_PREFIX, image['key'], image['ext']),
        image['data'], acl='public-read', mimetype=image['content_type'])
    for thumb in image['thumbs']:
        s3.put("%s%s-%s.%s" % (settings.AWS_IMAGEGALLERY_PREFIX, image['key'], thumb['size'], image['ext']),
            thumb['data'], acl='public-read', mimetype=image['content_type'])
    tags = image['tags']
    image = Image(key=image['key'], extension=image['ext'], hash=image['hash'],
      description='', album=album, photographer='', credits='', licence='',
      exif=image['exif'], uploader=user.get_profile(), width=image['width'],
      height=image['height'])
    image.save()
    for tag in [tag.lower() for tag in tags]:
        obj, created = Tag.objects.get_or_create(name=tag)
        image.tags.add(obj)

    return {'url': url, 'id': image.id}

def parse_image(file):
    key = generate_random_image_key()
    while Image.objects.filter(key=key).exists():
        # Potential weak spot here if the amount of objects
        # were to close in on the amount of available keys.
        key = generate_random_image_key()

    # TODO: Consider streaming the file instead of reading everything into memory first.
    # See simples3/htstream.py
    data = file.read()

    img = pil.open(StringIO(data))
    exif = {}
    if hasattr(img, '_getexif') and img._getexif() is not None:
        for tag, value in img._getexif().items():
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

    # Parse XMP-keywords
    from core import xmp
    xmp_dict = xmp.parse_xmp(data)
    keywords = xmp.keywords(xmp_dict) if xmp_dict is not None else []

    thumbs = []
    ext = file.name.split(".")[-1].lower()
    for size in settings.THUMB_SIZES:
        fp = StringIO()
        img_copy = img.copy()
        img_copy.thumbnail([size, size], pil.ANTIALIAS)
        # JPEG-files are very often named '.jpg', but PIL doesn't recognize that format
        img_copy.save(fp, "jpeg" if ext == "jpg" else ext)
        thumbs.append({'size': size, 'data': fp.getvalue()})

    return {'key': key, 'ext': ext, 'hash': sha1(data).hexdigest(),
      'width': img.size[0], 'height': img.size[1], 'content_type': file.content_type,
      'data': data, 'thumbs': thumbs, 'exif': json.dumps(exif),
      'tags': keywords}
