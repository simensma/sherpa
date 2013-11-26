# encoding: utf-8
from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator, InvalidPage
from django.db.models import Q

import json

from enrollment.models import State, Enrollment

def index(request):
    enrollments = Enrollment.get_active()

    if 'search' in request.GET:
        for q in request.GET['search'].split():
            enrollments = enrollments.filter(
                Q(address1__icontains=q) |
                Q(address2__icontains=q) |
                Q(address3__icontains=q) |
                Q(zipcode__icontains=q) |
                Q(area__icontains=q) |
                Q(users__name__icontains=q) |
                Q(users__phone__icontains=q) |
                Q(users__email__icontains=q) |
                Q(users__memberid__icontains=q) |
                Q(transactions__transaction_id__icontains=q) |
                Q(transactions__order_number__icontains=q)
            )

    enrollments = enrollments.prefetch_related('users', 'transactions', 'users__pending_user').order_by('-date_modified')
    paginator = Paginator(enrollments, 20)
    try:
        enrollments = paginator.page(request.GET.get('page', 1))
    except InvalidPage:
        enrollments = paginator.page(1)

    context = {
        'enrollments': enrollments,
        'search': request.GET.get('search'),
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
