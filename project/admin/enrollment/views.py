# encoding: utf-8
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

import json

from enrollment.models import State

@login_required
def index(request):
    context = {'state': State.objects.all()[0]}
    return render(request, 'admin/enrollment/index.html', context)

@login_required
def activate_state(request):
    if request.is_ajax():
        s = State.objects.all()[0]
        s.active = json.loads(request.POST['active'])
        s.save()
        return HttpResponse()

@login_required
def activate_card(request):
    if request.is_ajax():
        s = State.objects.all()[0]
        card = json.loads(request.POST['card'])
        s.card = card
        s.save()
        return HttpResponse()
