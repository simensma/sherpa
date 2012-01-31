from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from admin.models import Image, Album

def list_albums(request, album):
    albums = Album.objects.filter(parent=album)
    parents = []
    images = None
    if album is not None:
        images = Image.objects.filter(album=album)
        parents = list_parents(Album.objects.get(id=album))
    context = {'album': album, 'albums': albums, 'albumpath': parents, 'images': images}
    return render(request, 'admin/images/albums.html', context)

def image_details(request, image):
    image = Image.objects.get(id=image)
    parents = list_parents(image.album)
    context = {'image': image, 'albumpath': parents}
    return render(request, 'admin/images/image.html', context)

def delete_album(request, album):
    album = Album.objects.get(id=album)
    parents = list_parents(album)
    for album in parents:
        Image.objects.filter(album=album).delete()
        album.delete()
    return HttpResponseRedirect(reverse('admin.images.views.list_albums'))

def delete_image(request, image):
    image = Image.objects.get(id=image)
    image.delete()
    return HttpResponseRedirect(reverse('admin.images.views.list_albums', args=[image.album.id]))

def add_album(request, parent):
    if parent is not None:
        parent = Album.objects.get(id=parent)
    album = Album(name=request.POST['name'], parent=parent)
    album.save()
    return HttpResponseRedirect(reverse('admin.images.views.list_albums', args=[album.id]))

def list_parents(album):
    parents = []
    parents.append(album)
    while(album.parent != None):
        album = Album.objects.get(id=album.parent.id)
        parents.insert(0, album)
    return parents
