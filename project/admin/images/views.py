from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from admin.models import Image, Album
import random

from lib import S3
from local_settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

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
    context = {'image': image, 'albumpath': parents}
    return render(request, 'admin/images/image.html', context)

@login_required
def delete_album(request, album):
    album = Album.objects.get(id=album)
    parents = list_parents(album)
    for album in parents:
        Image.objects.filter(album=album).delete()
        album.delete()
    return HttpResponseRedirect(reverse('admin.images.views.list_albums'))

@login_required
def delete_image(request, image):
    image = Image.objects.get(id=image)
    image.delete()
    return HttpResponseRedirect(reverse('admin.images.views.list_albums', args=[image.album.id]))

@login_required
def add_album(request, parent):
    if parent is not None:
        parent = Album.objects.get(id=parent)
    album = Album(name=request.POST['name'], parent=parent)
    album.save()
    return HttpResponseRedirect(reverse('admin.images.views.list_albums', args=[album.id]))

def upload_image(request, album):
    if(request.method == 'GET'):
        parents = list_parents(Album.objects.get(id=album))
        context = {'albumpath': parents}
        return render(request, 'admin/images/upload.html', context)
    elif(request.method == 'POST'):
        for file in request.FILES.getlist('files'):
            key = generate_random_image_key()
            while Image.objects.filter(key=key).exists():
                # Potential weak spot here if the amount of objects
                # were to close in on the amount of available keys.
                key = generate_random_image_key()
            # Whoa! This S3-lib doesn't support streaming, so we'll have to read the whole
            # file into memory instead of streaming it to AWS. This might need to be
            # optimized at some point.
            conn = S3.AWSAuthConnection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
            result = conn.put('turistforeningen', "images/" + key, S3.S3Object(file.read()),
                {'x-amz-acl': 'public-read', 'Content-Type': file.content_type}
            )
            album = Album.objects.get(id=album)
            image = Image(key=key, hash='', description='', album=album, credits='', photographer='',
              photographer_contact='', uploader='todo', width=0, height=0)
            image.save()
        return HttpResponse(status=201)

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
