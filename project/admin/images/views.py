from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings

from admin.models import Image, Tag, Album
from lib import S3

from PIL.ExifTags import TAGS
import random, Image as pil
from cStringIO import StringIO
from hashlib import sha1
import json
from datetime import datetime

# Pixel sizes we'll want to generate thumbnail images for
# Note: A couple of places (the template, Image model etc.) has hardcoded
# these thumb sizes.
thumb_sizes = [500, 150]

@login_required
def list_albums(request, album):
    albums = Album.objects.filter(parent=album)
    parents = []
    images = None
    current_album = None
    if album is not None:
        current_album = Album.objects.get(id=album)
        images = Image.objects.filter(album=album)
        parents = list_parents(current_album)
    context = {'album': album, 'albums': albums, 'albumpath': parents,
               'current_album': current_album, 'images': images}
    return render(request, 'admin/images/albums.html', context)

@login_required
def image_details(request, image):
    image = Image.objects.get(id=image)
    parents = list_parents(image.album)
    exif = json.loads(image.exif)
    if exif.has_key('DateTime'):
        taken = datetime.strptime(exif['DateTime'], '%Y:%m:%d %H:%M:%S')
    else:
        taken = None
    tags = image.tags.all()
    context = {'image': image, 'albumpath': parents, 'exif': exif, 'taken': taken, 'tags': tags}
    return render(request, 'admin/images/image.html', context)

@login_required
def delete_items(request, album):
    Album.objects.filter(id__in=json.loads(request.POST['albums'])).delete()
    Image.objects.filter(id__in=json.loads(request.POST['images'])).delete()
    if(album is None):
        return HttpResponseRedirect(reverse('admin.images.views.list_albums'))
    else:
        album = Album.objects.get(id=album)
        return HttpResponseRedirect(reverse('admin.images.views.list_albums', args=[album.id]))

@login_required
def add_album(request, parent):
    if parent is not None:
        parent = Album.objects.get(id=parent)
    album = Album(name=request.POST['name'], parent=parent)
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
    if(parent is None):
        return HttpResponseRedirect(reverse('admin.images.views.list_albums'))
    else:
        return HttpResponseRedirect(reverse('admin.images.views.list_albums', args=[parent.id]))

@login_required
def update_images(request):
    images = Image.objects.filter(id__in=json.loads(request.POST['ids']))
    for image in images:
        if(request.POST['description'] != ""):
            image.description = request.POST['description']
        if(request.POST['photographer'] != ""):
            image.photographer = request.POST['photographer']
        if(request.POST['credits'] != ""):
            image.credits = request.POST['credits']
        if(request.POST['licence'] != ""):
            image.licence = request.POST['licence']
        image.save()
        # Note: Intentionally not removing old tags upon update.
        for tagName in json.loads(request.POST['tags-serialized']):
            tag = None
            try:
                tag = Tag.objects.get(name__iexact=tagName)
            except(Tag.DoesNotExist):
                tag = Tag(name=tagName)
            tag.save()
            tag.images.add(image)
    return HttpResponseRedirect(reverse('admin.images.views.list_albums', args=[images[0].album.id]))

@login_required
def filter_tags(request):
    tag_objects = Tag.objects.filter(name__startswith=request.GET['term'])
    tags = []
    for tag in tag_objects:
        tags.append(tag.name)
    return HttpResponse(json.dumps(tags))

@login_required
def upload_image(request, album):
    if(request.method == 'GET'):
        current_album = Album.objects.get(id=album)
        parents = list_parents(current_album)
        context = {'current_album': current_album, 'albumpath': parents}
        return render(request, 'admin/images/upload.html', context)
    elif(request.method == 'POST'):
        if(len(request.FILES.getlist('files')) == 0):
            return render(request, 'admin/images/iframe.html', {'result': 'no_files'})
        parsed_images = []
        ids = []
        for file in request.FILES.getlist('files'):
            key = generate_random_image_key()
            while Image.objects.filter(key=key).exists():
                # Potential weak spot here if the amount of objects
                # were to close in on the amount of available keys.
                key = generate_random_image_key()
            # Whoa! This S3-lib doesn't support streaming, so we'll have to read the whole
            # file into memory instead of streaming it to AWS. This might need to be
            # optimized at some point.
            data = file.read()

            # First parse and resize the images. This will consume a lot of memory.
            try:
                img = pil.open(StringIO(data))
                exif = {}
                if hasattr(img, '_getexif') and img._getexif() is not None:
                    for tag, value in img._getexif().items():
                        exif[TAGS.get(tag, tag)] = value
                thumbs = []
                ext = file.name.split(".")[-1]
                # JPEG-files are very often named '.jpg', but PIL doesn't recognize that format
                if(ext.lower() == "jpg"):
                    ext = "jpeg"
                for size in thumb_sizes:
                    fp = StringIO()
                    img_copy = img.copy()
                    img_copy.thumbnail([size, size])
                    img_copy.save(fp, ext)
                    thumbs.append({'size': size, 'data': fp.getvalue()})

                parsed_images.append({'key': key, 'hash': sha1(data).hexdigest(),
                  'width': img.size[0], 'height': img.size[1], 'content_type': file.content_type,
                  'data': data, 'thumbs': thumbs, 'exif': json.dumps(exif)})
            except(IOError, KeyError):
                # This is raised by PIL, maybe it was an invalid image file
                # or it didn't have the right file extension.
                return render(request, 'admin/images/iframe.html', {'result': 'parse_error'})

        # Done parsing, now we'll start moving stuff into persistant state
        # (Local database entry + store image and thumbs on S3)
        album = Album.objects.get(id=album)
        for image in parsed_images:
            conn = S3.AWSAuthConnection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
            conn.put(settings.AWS_BUCKET, settings.AWS_IMAGEGALLERY_PREFIX + image['key'],
                S3.S3Object(image['data']),
                {'x-amz-acl': 'public-read', 'Content-Type': image['content_type']}
            )
            for thumb in image['thumbs']:
                conn.put(settings.AWS_BUCKET, settings.AWS_IMAGEGALLERY_PREFIX + image['key'] + "-" + str(thumb['size']),
                    S3.S3Object(thumb['data']),
                    {'x-amz-acl': 'public-read', 'Content-Type': image['content_type']}
                )
            image = Image(key=image['key'], hash=image['hash'], description='', album=album,
              photographer='', credits='', licence='', exif=image['exif'],
              uploader=request.user.get_profile(), width=image['width'], height=image['height'])
            image.save()
            ids.append(image.id)
        return render(request, 'admin/images/iframe.html', {'result': 'success', 'ids': json.dumps(ids)})

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
