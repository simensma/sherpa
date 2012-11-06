from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from association.models import Association

def index(request):
    return render(request, 'main/admin/dashboard.html')

def set_active_association(request, association):
    # Note: this object will be copied in session for a while and will NOT get updated even if the original object is.
    request.session['active_association'] = Association.objects.get(id=association)
    if request.META.get('HTTP_REFERER') != None:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponseRedirect(reverse('admin.views.index'))
