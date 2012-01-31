#from django.core.urlresolvers import reverse
#from django.http import HttpResponseRedirect
from django.shortcuts import render
from admin.models import Album

def dashboard(request, album):
    albums = Album.objects.filter(parent=album)
    context = {'albums': albums, 'parents': parents}
    return render(request, 'admin/images/dashboard.html', context)
