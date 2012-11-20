# encoding: utf-8
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader
from django.core.mail import send_mail

from datetime import datetime
from smtplib import SMTPDataError
import json

from enrollment.models import Giver, Receiver, membership_types

EMAIL_RECIPIENT = "DNT medlemsservice <medlem@turistforeningen.no>"
EMAIL_FROM = "Den Norske Turistforening <medlem@turistforeningen.no>"
EMAIL_SUBJECT = "Gavemedlemskap"

def index(request):
    if 'gift_membership' in request.session:
        if 'order_sent' in request.session['gift_membership']:
            return HttpResponseRedirect(reverse('enrollment.views_gift.receipt'))
        return HttpResponseRedirect(reverse('enrollment.views_gift.form'))
    return render(request, 'enrollment/gift/index.html')

def form(request):
    if not 'gift_membership' in request.session:
        request.session['gift_membership'] = {}
    if 'order_sent' in request.session['gift_membership']:
        return HttpResponseRedirect(reverse('enrollment.views_gift.receipt'))

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

    if 'giver' in request.session['gift_membership']:
        if not request.session['gift_membership']['giver'].validate():
            context['invalid_input'] = True

    if 'receivers' in request.session['gift_membership']:
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
    if not 'gift_membership' in request.session:
        return HttpResponseRedirect(reverse('enrollment.views_gift.index'))
    if 'order_sent' in request.session['gift_membership']:
        return HttpResponseRedirect(reverse('enrollment.views_gift.receipt'))

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

    request.session['gift_membership'] = {
        'giver': giver,
        'receivers': receivers,
        'any_normal_memberships': any(r.type['code'] == 'normal' for r in receivers)}

    if not giver.validate():
        return HttpResponseRedirect(reverse('enrollment.views_gift.form'))
    for receiver in receivers:
        if not receiver.validate():
            return HttpResponseRedirect(reverse('enrollment.views_gift.form'))

    return HttpResponseRedirect(reverse('enrollment.views_gift.confirm'))

def confirm(request):
    if not 'gift_membership' in request.session:
        return HttpResponseRedirect(reverse('enrollment.views_gift.index'))
    if 'order_sent' in request.session['gift_membership']:
        return HttpResponseRedirect(reverse('enrollment.views_gift.receipt'))

    context = {
        'giver': request.session['gift_membership']['giver'],
        'receivers': request.session['gift_membership']['receivers'],
        'any_normal_memberships': request.session['gift_membership']['any_normal_memberships']
    }
    return render(request, 'enrollment/gift/confirm.html', context)

def send(request):
    if not 'gift_membership' in request.session:
        return HttpResponseRedirect(reverse('enrollment.views_gift.index'))
    email_recipients = []
    t = loader.get_template('enrollment/gift/email.html')
    c = RequestContext(request, {
        'giver': request.session['gift_membership']['giver'],
        'receivers': request.session['gift_membership']['receivers']
    })
    message = t.render(c)
    send_mail(EMAIL_SUBJECT, message, EMAIL_FROM, [EMAIL_RECIPIENT])
    request.session['gift_membership']['order_sent'] = True
    request.session.modified = True
    return HttpResponseRedirect(reverse('enrollment.views_gift.receipt'))

def receipt(request):
    if not 'gift_membership' in request.session:
        return HttpResponseRedirect(reverse('enrollment.views_gift.index'))
    context = {
        'giver': request.session['gift_membership']['giver'],
        'receivers': request.session['gift_membership']['receivers'],
        'any_normal_memberships': request.session['gift_membership']['any_normal_memberships']
    }
    return render(request, 'enrollment/gift/receipt.html', context)

def clear(request):
    del request.session['gift_membership']
    return HttpResponseRedirect(reverse('enrollment.views_gift.index'))
