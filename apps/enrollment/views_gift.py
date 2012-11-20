# encoding: utf-8
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader
from django.core.mail import send_mail

from datetime import datetime
from smtplib import SMTPDataError
import json

from core import validator
from core.models import Zipcode

EMAIL_RECIPIENT = "DNT medlemsservice <medlem@turistforeningen.no>"
EMAIL_FROM = "Den Norske Turistforening <medlem@turistforeningen.no>"
EMAIL_SUBJECT = "Gavemedlemskap"

# Hardcoded ages
AGE_SENIOR = 67
AGE_MAIN = 27
AGE_STUDENT = 19
AGE_SCHOOL = 13

membership_types = [
  {'name': 'Vanlig medlemskap', 'price': None},
  {'name': 'Dåpsgave', 'price': 900},
  {'name': 'Jubileum', 'price': 5500},
  {'name': 'Livsvarig medlemskap', 'price': 13750},
]

class Giver():
    def __init__(self, name, address, zipcode, memberno, phone, email):
        self.name = name
        self.address = address
        self.zipcode = zipcode
        try:
            self.area = Zipcode.objects.get(zipcode=zipcode).area
        except Zipcode.DoesNotExist:
            self.area = ''
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

        if self.area == '':
            return False

        if not validator.memberno(self.memberno, req=False):
            return False

        if not validator.phone(self.phone, req=False):
            return False

        if not validator.email(self.email, req=False):
            return False

        if not Zipcode.objects.filter(zipcode=self.zipcode).exists():
            return False

        return True

class Receiver():
    def __init__(self, type, name, dob, address, zipcode, phone, email):
        self.type_index = int(type)
        self.type = membership_types[self.type_index]
        self.name = name
        try:
            self.dob = datetime.strptime(dob, "%d.%m.%Y")
        except ValueError:
            self.dob = None
        self.address = address
        self.zipcode = zipcode
        try:
            self.area = Zipcode.objects.get(zipcode=zipcode).area
        except Zipcode.DoesNotExist:
            self.area = ''
        self.phone = phone
        self.email = email

    def validate(self):
        if self.type_index < 0 or self.type_index >= len(membership_types):
            return False

        if not validator.name(self.name):
            return False

        if not isinstance(self.dob, datetime):
            return False

        if not validator.address(self.address):
            return False

        if not validator.zipcode(self.zipcode):
            return False

        if self.area == '':
            return False

        if not validator.phone(self.phone, req=False):
            return False

        if not validator.email(self.email, req=False):
            return False

        if not Zipcode.objects.filter(zipcode=self.zipcode).exists():
            return False

        return True

def index(request):
    if 'gift_membership' in request.session:
        return HttpResponseRedirect(reverse('enrollment.views_gift.form'))
    return render(request, 'enrollment/gift/index.html')

def form(request):
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

    if request.session['gift_membership'].has_key('receivers'):
        for receiver in request.session['gift_membership']['receivers']:
            if not receiver.validate():
                context['invalid_input'] = True

    context.update({
        'days': range(1, 32),
        'months': months,
        'years': reversed(range(1900, datetime.now().year + 1)),
        'types': membership_types,
        'giver': request.session['gift_membership'].get('giver', None),
        'receivers': request.session['gift_membership'].get('receivers', []),
        'chosen_type': int(request.POST.get('type', -1)),
    })
    return render(request, 'enrollment/gift/form.html', context)

def validate(request):
    if not request.session.has_key('gift_membership'):
        return HttpResponseRedirect(reverse('enrollment.views.form'))

    giver = Giver(
        request.POST['giver_name'],
        request.POST['giver_address'],
        request.POST['giver_zipcode'],
        request.POST['giver_memberno'],
        request.POST['giver_phone'],
        request.POST['giver_email'])

    receivers = []
    for r in json.loads(request.POST['receivers']):
        receivers.append(Receiver(
            r['type'],
            r['name'],
            r['dob'],
            r['address'],
            r['zipcode'],
            r['phone'],
            r['email']
            ))

    request.session['gift_membership'] = {'giver': giver, 'receivers': receivers}
    if not giver.validate():
        return HttpResponseRedirect(reverse('enrollment.views_gift.form'))
    for receiver in receivers:
        if not receiver.validate():
            return HttpResponseRedirect(reverse('enrollment.views_gift.form'))

    return HttpResponseRedirect(reverse('enrollment.views_gift.confirm'))

def confirm(request):
    if not request.session.has_key('gift_membership'):
        return HttpResponseRedirect(reverse('enrollment.views.form'))

    context = {
        'giver': request.session['gift_membership']['giver'],
        'receivers': request.session['gift_membership']['receivers']
    }
    return render(request, 'enrollment/gift/confirm.html', context)

def send(request):
    email_recipients = []
    t = loader.get_template('enrollment/gift/email.html')
    c = RequestContext(request, {
        'giver': request.session['gift_membership']['giver'],
        'receivers': request.session['gift_membership']['receivers']
    })
    message = t.render(c)
    send_mail(EMAIL_SUBJECT, message, EMAIL_FROM, [EMAIL_RECIPIENT])
    return HttpResponse()
