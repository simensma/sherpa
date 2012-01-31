#from django.core.urlresolvers import reverse
#from django.http import HttpResponseRedirect
from django.shortcuts import render
from admin.models import Image, Album

def albums(request, album):
    albums = Album.objects.filter(parent=album)
    parents = []
    images = None
    if album is not None:
        images = Image.objects.filter(album=album)
        parents = list_parents(Album.objects.get(id=album))
    context = {'albums': albums, 'albumpath': parents, 'images': images}
    return render(request, 'admin/images/albums.html', context)

def image(request, image):
    image = Image.objects.get(id=image)
    parents = list_parents(image.album)
    context = {'image': image, 'albumpath': parents}
    return render(request, 'admin/images/image.html', context)

def list_parents(album):
    parents = []
    parents.append(album)
    while(album.parent != None):
        album = Album.objects.get(id=album.parent.id)
        parents.insert(0, album)
    return parents
