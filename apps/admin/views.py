from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied

from association.models import Association

def index(request):
    return render(request, 'main/admin/dashboard.html')

def set_active_association(request, association):
    # Note: this object will be copied in session for a while and will NOT get updated even if the original object is.
    association = Association.objects.get(id=association)
    if not association in request.user.get_profile().associations.all():
        raise PermissionDenied

    request.session['active_association'] = association
    if request.META.get('HTTP_REFERER') != None:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponseRedirect(reverse('admin.views.index'))
