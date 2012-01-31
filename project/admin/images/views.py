#from django.core.urlresolvers import reverse
#from django.http import HttpResponseRedirect
from django.shortcuts import render
from admin.models import Album

def dashboard(request, album):
    albums = Album.objects.filter(parent=album)
    parents = []
    if album is not None:
        album = Album.objects.get(id=album)
        parents.append(album)
        while(album.parent != None):
            album = Album.objects.get(id=album.parent.id)
            parents.insert(0, album)

    context = {'albums': albums, 'albumpath': parents}
    return render(request, 'admin/images/dashboard.html', context)
