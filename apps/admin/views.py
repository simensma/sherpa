from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from association.models import Association

def index(request):
    return render(request, 'admin/dashboard.html')

def set_active_association(request, association):
    request.session['active_association'] = Association.objects.get(id=association)
    if request.META.get('REFERER') != None:
        return HttpResponseRedirect(request.META.get('REFERER'))
    else:
        return HttpResponseRedirect(reverse('admin.views.index'))
