# encoding: utf-8
from django.shortcuts import render
from django.http import HttpResponse

import json

from enrollment.models import State, Enrollment

def index(request):
    context = {
        # TODO: Sort sensibly
        'enrollments': Enrollment.get_active().prefetch_related('users', 'transactions', 'users__pending_user')
    }
    return render(request, 'common/admin/enrollment/index.html', context)

def status(request):
    context = {'state': State.objects.all()[0]}
    return render(request, 'common/admin/enrollment/status.html', context)

def activate_state(request):
    if request.is_ajax():
        s = State.objects.all()[0]
        s.active = json.loads(request.POST['active'])
        s.save()
        return HttpResponse()

def activate_card(request):
    if request.is_ajax():
        s = State.objects.all()[0]
        card = json.loads(request.POST['card'])
        s.card = card
        s.save()
        return HttpResponse()
