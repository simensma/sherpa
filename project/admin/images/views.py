#from django.core.urlresolvers import reverse
#from django.http import HttpResponseRedirect
from django.shortcuts import render
from admin.models import Image, Album

def dashboard(request, album):
    albums = Album.objects.filter(parent=album)
    parents = []
    images = None
    if album is not None:
        images = Image.objects.filter(album=album)
        album = Album.objects.get(id=album)
        parents.append(album)
        while(album.parent != None):
            album = Album.objects.get(id=album.parent.id)
            parents.insert(0, album)

    context = {'albums': albums, 'albumpath': parents, 'images': images}
    return render(request, 'admin/images/dashboard.html', context)

def image(request, image):
    return None
