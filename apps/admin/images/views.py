from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db.models import Q

from core.models import Tag
from admin.models import Image, Album

from PIL.ExifTags import TAGS
import random, Image as pil
from cStringIO import StringIO
from hashlib import sha1
import json
from datetime import datetime
import simples3

SPEED_UPLOAD_ALBUM_NAME = "Brukeralbum"

def createUserAlbum(user):
    #create user album if it dosent exist
    user_name = user.first_name + " " + user.last_name

    #get or create useruploads album
    try:
        user_root = Album.objects.get(name=SPEED_UPLOAD_ALBUM_NAME, parent=None)
    except ObjectDoesNotExist:
        user_root = Album(name=SPEED_UPLOAD_ALBUM_NAME)
        user_root.save()

    #get or create user album in useruploads album
    #if two users share name, they share album, this could be changed by using email
    try:
        user_album = Album.objects.get(name=user_name, parent=user_root)
    except ObjectDoesNotExist:
        user_album = Album(name=user_name, parent=user_root)
        user_album.save()
    return user_album;

@login_required
def fast_upload(request):
    user_album = createUserAlbum(request.user)

    try:
        file = request.FILES['file']
    except KeyError:
        return render(request, 'admin/images/iframe.html', {'result': 'no_files'})

    #parse file
    try:
        parsed_image = parse_image(file)
    except(IOError, KeyError):
        return render(request, 'admin/images/iframe.html', {'result': 'parse_error'})

    #store stuff on s3 and in db
    stored_image = store_image(parsed_image, user_album, request.user)

    #add info to image
    image = Image.objects.get(id=stored_image['id'])
    tags = json.loads(request.POST['tags-serialized'])
    add_info_to_image(image, request.POST['description'], request.POST['photographer'], request.POST['credits'], request.POST['licence'], tags)

    return render(request, 'admin/images/iframe.html', {'result': 'success', 'url': stored_image['url'], })

@login_required
def list_albums(request, album):
    #create user album if it dosent exist
    createUserAlbum(request.user)

    albums = Album.objects.filter(parent=album).order_by('name')
    parents = []
    images = None
    current_album = None
    if album is not None:
        current_album = Album.objects.get(id=album)
        images = Image.objects.filter(album=album)
        parents = list_parents(current_album)
    context = {'album': album, 'albums': albums, 'albumpath': parents,
               'current_album': current_album, 'images': images,
               'aws_bucket': settings.AWS_BUCKET}
    return render(request, 'admin/images/albums.html', context)

@login_required
def image_details(request, image):
    image = Image.objects.get(id=image)
    parents = list_parents(image.album)
    exif = json.loads(image.exif)
    try:
        taken = datetime.strptime(exif['DateTime'], '%Y:%m:%d %H:%M:%S')
    except Exception:
        taken = None
    tags = image.tags.all()
    context = {'image': image, 'albumpath': parents, 'exif': exif, 'taken': taken, 'tags': tags,
        'aws_bucket': settings.AWS_BUCKET}
    return render(request, 'admin/images/image.html', context)

@login_required
def delete_items(request, album):
    Album.objects.filter(id__in=json.loads(request.POST['albums'])).delete()
    Image.objects.filter(id__in=json.loads(request.POST['images'])).delete()
    if album is None:
        return HttpResponseRedirect(reverse('admin.images.views.list_albums'))
    else:
        album = Album.objects.get(id=album)
        return HttpResponseRedirect(reverse('admin.images.views.list_albums', args=[album.id]))

@login_required
def add_album(request, parent):
    albumname = request.POST['name']
    if parent is not None:
        parent = Album.objects.get(id=parent)
    elif albumname == SPEED_UPLOAD_ALBUM_NAME:
        #ensure unique name if the name is the same as user-uploads
        res = Album.objects.filter(name=request.POST['name'], parent=None)
        albumname = albumname + str(len(res)+1)

    album = Album(name=albumname, parent=parent)
    album.save()
    if parent is None:
        return HttpResponseRedirect(reverse('admin.images.views.list_albums'))
    else:
        return HttpResponseRedirect(reverse('admin.images.views.list_albums', args=[parent.id]))

@login_required
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

@login_required
def update_images(request):
    images = Image.objects.filter(id__in=json.loads(request.POST['ids']))
    for image in images:
        tags = json.loads(request.POST['tags-serialized'])
        add_info_to_image(image, request.POST['description'], request.POST['photographer'], request.POST['credits'], request.POST['licence'], tags)
    return HttpResponseRedirect(reverse('admin.images.views.list_albums', args=[images[0].album.id]))

@login_required
def upload_image(request, album):
    if request.method == 'GET':
        current_album = Album.objects.get(id=album)
        parents = list_parents(current_album)
        context = {'current_album': current_album, 'albumpath': parents}
        return render(request, 'admin/images/upload.html', context)
    elif request.method == 'POST':
        if len(request.FILES.getlist('files')) == 0:
            return render(request, 'admin/images/iframe.html', {'result': 'no_files'})

        #parsing
        parsed_images = []
        for file in request.FILES.getlist('files'):
            try:
                parsed_images.append(parse_image(file))
            except(IOError, KeyError):
                return render(request, 'admin/images/iframe.html', {'result': 'parse_error'})

        #storing
        ids = []
        album = Album.objects.get(id=album)
        for image in parsed_images:
            stored_image = store_image(image, album, request.user)
            ids.append(stored_image['id'])
        return render(request, 'admin/images/iframe.html', {'result': 'success', 'ids': json.dumps(ids)})

def content_json(request, album):
    if album is not None:
        current_album = Album.objects.get(id=album)
        objects = parse_objects(list_parents(current_album),
            Album.objects.filter(parent=album).order_by('name'),
            Image.objects.filter(album=album))
    else:
        objects = parse_objects([], Album.objects.filter(parent=None).order_by('name'), [])
    return HttpResponse(json.dumps(objects))

def search_json(request):
    images = []
    if len(request.POST['query']) >= settings.IMAGE_SEARCH_LENGTH:
        for word in request.POST['query'].split(' '):
            images += Image.objects.filter(
                Q(description__icontains=word) |
                Q(album__name__icontains=word) |
                Q(photographer__icontains=word) |
                Q(credits__icontains=word) |
                Q(licence__icontains=word) |
                Q(exif__icontains=word) |
                Q(uploader__user__first_name__icontains=word) |
                Q(uploader__user__last_name__icontains=word) |
                Q(uploader__user__email__icontains=word) |
                Q(tags__name__icontains=word)
        )
    objects = parse_objects([], [], images)
    return HttpResponse(json.dumps(objects))

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
    while(album.parent != None):
        album = Album.objects.get(id=album.parent.id)
        parents.insert(0, album)
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
    image = Image(key=image['key'], extension=image['ext'], hash=image['hash'],
      description='', album=album, photographer='', credits='', licence='',
      exif=image['exif'], uploader=user.get_profile(), width=image['width'],
      height=image['height'])
    image.save()
    return {'url':url, 'id':image.id};

def parse_image(file):
    key = generate_random_image_key()
    while Image.objects.filter(key=key).exists():
        # Potential weak spot here if the amount of objects
        # were to close in on the amount of available keys.
        key = generate_random_image_key()

    # Consider streaming the file instead of reading everything into memory first.
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
      'data': data, 'thumbs': thumbs, 'exif': json.dumps(exif)}

def add_info_to_image(image, description, photographer, credits, licence, tags):
    if description != "":
        image.description = description
    if photographer != "":
        image.photographer = photographer
    if credits != "":
        image.credits = credits
    if licence != "":
        image.licence = licence

    image.save()
    # Note: Intentionally not removing old tags upon update.
    for tagName in tags:
        tag = None
        try:
            tag = Tag.objects.get(name__iexact=tagName)
        except(Tag.DoesNotExist):
            tag = Tag(name=tagName)
        tag.save()
        tag.images.add(image)