# encoding: utf-8
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

import json

from enrollment.models import State

@login_required
def index(request):
    context = {'enrollment_activated': State.objects.all()[0].active}
    return render(request, 'admin/enrollment/index.html', context)

@login_required
def activate(request):
    if request.is_ajax():
        s = State.objects.all()[0]
        s.active = json.loads(request.POST['active'])
        s.save()
        return HttpResponse()
