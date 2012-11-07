from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied

from association.models import Association

def index(request):
    return render(request, 'common/admin/dashboard.html')
