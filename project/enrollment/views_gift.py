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

class Invalid(Exception):
    pass

class Giver():
    def __init__(self, name, address, zipcode, memberno, phone, email):
        try:
            self.name = name
            self.address = address
            self.zipcode = zipcode
            self.location = Zipcode.objects.get(zipcode=zipcode).location
            self.memberno = memberno
            self.phone = phone
            self.email = email

            if not validator.name(name):
                raise Invalid('Invalid name')

            if not validator.address(address):
                raise Invalid('Invalid address')

            if not validator.zipcode(zipcode):
                raise Invalid('Invalid zipcode')

            if not validator.memberno(memberno):
                raise Invalid('Invalid memberno')

            if not validator.phone(phone):
                raise Invalid('Invalid phone')

            if not validator.email(email):
                raise Invalid('Invalid email')

        except Zipcode.DoesNotExist:
            raise Invalid('Invalid zipcode')

def index(request):
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

    if request.session.has_key('gift_membership.invalid_input'):
        del request.session['gift_membership.invalid_input']
        context['invalid_input'] = True

    context.update({
        'days': range(1, 32),
        'months': months,
        'years': reversed(range(1900, datetime.now().year + 1)),
        'types': membership_types,
    })
    return render(request, 'enrollment/gift/index.html', context)

def validate(request):
    try:
        giver = Giver(
            request.POST['giver_name'],
            request.POST['giver_address'],
            request.POST['giver_zipcode'],
            request.POST['giver_memberno'],
            request.POST['giver_phone'],
            request.POST['giver_email'])
    except Invalid:
        request.session['gift_membership.invalid_input'] = True
        return HttpResponseRedirect(reverse('enrollment.views_gift.index'))
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
