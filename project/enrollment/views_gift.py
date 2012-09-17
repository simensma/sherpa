# encoding: utf-8
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from datetime import datetime
from smtplib import SMTPDataError
import json

from user.models import Zipcode

EMAIL_FROM = "Den Norske Turistforening <medlem@turistforeningen.no>"
EMAIL_SUBJECT = "Gavemedlemskap"

# Hardcoded ages
AGE_SENIOR = 67
AGE_MAIN = 27
AGE_STUDENT = 19
AGE_SCHOOL = 13

membership_types = [
  'Vanlig medlemskap',
  'Dåpsgave (kr. 900)',
  'Jubileum (kr. 5500)',
  'Livsvarig medlemskap (kr. 13750)',
]

def index(request):
    months = zip(range(1, 13), [
        'Januar',
        'Februar',
        'Mars',
        'April',
        'Mai',
        'Juni',
        'Juli',
        'August',
        'September',
        'Oktober',
        'November',
        'Desember'
    ])
    context = {
        'days': range(1, 32),
        'months': months,
        'years': reversed(range(1900, datetime.now().year + 1)),
        'types': membership_types,
    }
    return render(request, 'enrollment/gift/index.html', context)

def validate(request):
    giver = {
        'name': request.POST['giver_name'],
        'address': request.POST['giver_address'],
        'zipcode': request.POST['giver_zipcode'],
        'location': Zipcode.objects.get(zipcode=request.POST['giver_zipcode']).location,
        'memberno': request.POST['giver_memberno'],
        'phone': request.POST['giver_phone'],
        'email': request.POST['giver_email'],
    }
    receivers = json.loads(request.POST['receivers'])
    for receiver in receivers:
        receiver['type'] = membership_types[int(receiver['type'])]

    # Todo: Validations

    request.session['gift_membership'] = {'giver': giver, 'receivers': receivers}
    return HttpResponseRedirect(reverse('enrollment.views_gift.confirm'))

def confirm(request):
    context = {
        'giver': request.session['gift_membership']['giver'],
        'receivers': request.session['gift_membership']['receivers']
    }
    return render(request, 'enrollment/gift/confirm.html', context)

def send(request):
    return HttpResponse()
