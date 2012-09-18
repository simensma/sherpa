# encoding: utf-8
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from datetime import datetime
from smtplib import SMTPDataError
import json

from core import validator
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

class Giver():
    def __init__(self, name, address, zipcode, memberno, phone, email):
        self.name = name
        self.address = address
        self.zipcode = zipcode
        try:
            self.location = Zipcode.objects.get(zipcode=zipcode).location
        except Zipcode.DoesNotExist:
            self.location = None
        self.memberno = memberno
        self.phone = phone
        self.email = email

    def validate(self):
        if not validator.name(self.name):
            return False

        if not validator.address(self.address):
            return False

        if not validator.zipcode(self.zipcode):
            return False

        if self.location == None:
            return False

        if not validator.memberno(self.memberno):
            return False

        if not validator.phone(self.phone):
            return False

        if not validator.email(self.email):
            return False

        if not Zipcode.objects.filter(zipcode=self.zipcode).exists():
            return False

        return True

def index(request):
    if not request.session.has_key('gift_membership'):
        request.session['gift_membership'] = {}

    context = {}
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

    if request.session['gift_membership'].has_key('giver'):
        if not request.session['gift_membership']['giver'].validate():
            context['invalid_input'] = True

    context.update({
        'days': range(1, 32),
        'months': months,
        'years': reversed(range(1900, datetime.now().year + 1)),
        'types': membership_types,
        'giver': request.session['gift_membership'].get('giver', None),
    })
    return render(request, 'enrollment/gift/index.html', context)

def validate(request):
    if not request.session.has_key('gift_membership'):
        return HttpResponseRedirect(reverse('enrollment.views.index'))

    giver = Giver(
        request.POST['giver_name'],
        request.POST['giver_address'],
        request.POST['giver_zipcode'],
        request.POST['giver_memberno'],
        request.POST['giver_phone'],
        request.POST['giver_email'])

    receivers = json.loads(request.POST['receivers'])
    for receiver in receivers:
        receiver['type'] = membership_types[int(receiver['type'])]

    # Todo: Receiver validations

    request.session['gift_membership'] = {'giver': giver, 'receivers': receivers}
    if not giver.validate():
        return HttpResponseRedirect("%s#skjema" % reverse('enrollment.views_gift.index'))
    return HttpResponseRedirect(reverse('enrollment.views_gift.confirm'))

def confirm(request):
    if not request.session.has_key('gift_membership'):
        return HttpResponseRedirect(reverse('enrollment.views.index'))

    context = {
        'giver': request.session['gift_membership']['giver'],
        'receivers': request.session['gift_membership']['receivers']
    }
    return render(request, 'enrollment/gift/confirm.html', context)

def send(request):
    return HttpResponse()
