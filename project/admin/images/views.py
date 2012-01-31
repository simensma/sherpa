#from django.core.urlresolvers import reverse
#from django.http import HttpResponseRedirect
from django.shortcuts import render
from admin.models import Album

def dashboard(request):
    albums = Album.objects.all()
    context = {'albums': albums}
    return render(request, 'admin/images/dashboard.html', context)
