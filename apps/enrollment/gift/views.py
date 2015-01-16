# encoding: utf-8
from smtplib import SMTPException
from ssl import SSLError
from datetime import date
import json
import logging
import sys

from django.shortcuts import render, redirect
from django.template import RequestContext, loader
from django.core.mail import send_mail
from django.contrib import messages

from enrollment.gift.models import Giver, Receiver, membership_types, membership_price_by_code

logger = logging.getLogger('sherpa')

EMAIL_FROM_MEMBERSERVICE = "Den Norske Turistforening <no-reply@turistforeningen.no>" # The "from"-address in the email going to our memberservice
EMAIL_FROM_GIVER = "Den Norske Turistforening <medlem@turistforeningen.no>" # The "from"-address in the email going to the giver making the order
EMAIL_MEMBERSERVICE_RECIPIENT = "DNT medlemsservice <medlem@turistforeningen.no>"
EMAIL_MEMBERSERVICE_SUBJECT = u"Bestilling av gavemedlemskap"
EMAIL_GIVER_SUBJECT = u"Kvittering på bestilling av gavemedlemskap"

# You might want to re-use this for the following years, however it's not set to automatically display (yet)!
CHRISTMAS_WARNING_END = date(2013, 12, 24)

def index(request):
    if 'gift_membership' in request.session and 'order_sent' in request.session['gift_membership']:
        return redirect('enrollment.gift.views.receipt')
    context = {
        'prices': membership_price_by_code,
        'display_christmas_warning': date.today() <= CHRISTMAS_WARNING_END
    }
    return render(request, 'central/enrollment/gift/index.html', context)

def form(request):
    if not 'gift_membership' in request.session:
        request.session['gift_membership'] = {}
    if 'order_sent' in request.session['gift_membership']:
        return redirect('enrollment.gift.views.receipt')

    if 'giver' in request.session['gift_membership']:
        request.session['gift_membership']['giver'].validate(request, add_messages=True)

    if 'receivers' in request.session['gift_membership']:
        for receiver in request.session['gift_membership']['receivers']:
            receiver.validate(request, add_messages=True)

    if 'type' in request.POST:
        # We had some error where type was set to the empty string. Not sure how
        # that can happen (it was with Firefox 20.0), but the type isn't that
        # important so just ignore this error.
        # If you want to, see https://sentry.turistforeningen.no/turistforeningen/sherpa/group/127/events/
        try:
            chosen_type = int(request.POST['type'])
        except ValueError:
            chosen_type = None
    else:
        chosen_type = None

    context = {
        'types': membership_types,
        'giver': request.session['gift_membership'].get('giver', None),
        'receivers': request.session['gift_membership'].get('receivers', []),
        'chosen_type': chosen_type,
        'display_christmas_warning': date.today() <= CHRISTMAS_WARNING_END,
    }
    return render(request, 'central/enrollment/gift/form.html', context)

def validate(request):
    # TODO: Use the django form API
    if not 'gift_membership' in request.session:
        return redirect('enrollment.gift.views.index')
    if 'order_sent' in request.session['gift_membership']:
        return redirect('enrollment.gift.views.receipt')
    if request.method != 'POST' or not 'receivers' in request.POST:
        return redirect('enrollment.gift.views.form')

    giver = Giver(
        request.POST['giver_name'].strip(),
        request.POST['giver_address'].strip(),
        request.POST['giver_zipcode'].strip(),
        request.POST['giver_memberid'].strip(),
        request.POST['giver_phone'].strip(),
        request.POST['giver_email'].strip(),
    )

    receivers = []
    try:
        for r in json.loads(request.POST['receivers']):
            receivers.append(Receiver(
                r['type'].strip(),
                r['name'].strip(),
                r['dob'].strip(),
                r['address'].strip(),
                r['zipcode'].strip(),
                r['phone'].strip(),
                r['email'].strip(),
            ))
    except ValueError:
        # Something wrong with the json-formatted POST value. Not quite sure how this can happen, see:
        # https://sentry.turistforeningen.no/turistforeningen/sherpa/group/885/
        return redirect('enrollment.gift.views.form')

    request.session['gift_membership'] = {
        'giver': giver,
        'receivers': receivers,
        'any_normal_memberships': any(r.type['code'] == 'normal' for r in receivers)
    }

    form_valid = giver.validate()
    for receiver in receivers:
        form_valid = form_valid and receiver.validate()
    if not form_valid:
        return redirect('enrollment.gift.views.form')

    return redirect('enrollment.gift.views.confirm')

def confirm(request):
    if not 'gift_membership' in request.session:
        return redirect('enrollment.gift.views.index')
    if not 'giver' in request.session['gift_membership']:
        # Not quite sure how this can happen, see:
        # https://sentry.turistforeningen.no/turistforeningen/sherpa/group/1262/
        return redirect('enrollment.gift.views.form')
    if 'order_sent' in request.session['gift_membership']:
        return redirect('enrollment.gift.views.receipt')

    form_valid = request.session['gift_membership']['giver'].validate()
    for receiver in request.session['gift_membership']['receivers']:
        form_valid = form_valid and receiver.validate()
    if not form_valid:
        return redirect('enrollment.gift.views.form')

    context = {
        'giver': request.session['gift_membership']['giver'],
        'receivers': request.session['gift_membership']['receivers'],
        'display_christmas_warning': date.today() <= CHRISTMAS_WARNING_END
    }
    return render(request, 'central/enrollment/gift/confirm.html', context)

def send(request):
    if not 'gift_membership' in request.session:
        return redirect('enrollment.gift.views.index')
    t1 = loader.get_template('central/enrollment/gift/emails/memberservice.txt')
    t2 = loader.get_template('central/enrollment/gift/emails/giver.txt')
    # Note that this context is used for both email templates
    c = RequestContext(request, {
        'giver': request.session['gift_membership']['giver'],
        'receivers': request.session['gift_membership']['receivers']
    })
    memberservice_message = t1.render(c)
    giver_message = t2.render(c)

    try:
        send_mail(EMAIL_MEMBERSERVICE_SUBJECT, memberservice_message, EMAIL_FROM_MEMBERSERVICE, [EMAIL_MEMBERSERVICE_RECIPIENT])
    except (SMTPException, SSLError):
        logger.warning(u"Klarte ikke å sende gavemedlemskap-epost til medlemsservice",
            exc_info=sys.exc_info(),
            extra={'request': request}
        )
        messages.error(request, 'email_memberservice_fail')
        return redirect('enrollment.gift.views.confirm')

    if request.session['gift_membership']['giver'].email != '':
        try:
            send_mail(EMAIL_GIVER_SUBJECT, giver_message, EMAIL_FROM_GIVER, ['"%s" <%s>' % (request.session['gift_membership']['giver'].name, request.session['gift_membership']['giver'].email)])
        except (SMTPException, SSLError):
            logger.warning(u"Klarte ikke å sende gavemedlemskapskvittering på e-post",
                exc_info=sys.exc_info(),
                extra={'request': request}
            )
            messages.error(request, 'email_receipt_fail')
    request.session['gift_membership']['order_sent'] = True
    request.session.modified = True
    return redirect('enrollment.gift.views.receipt')

def receipt(request):
    if not 'gift_membership' in request.session:
        return redirect('enrollment.gift.views.index')
    if not 'giver' in request.session['gift_membership']:
        return redirect('enrollment.gift.views.form')
    context = {
        'giver': request.session['gift_membership']['giver'],
        'receivers': request.session['gift_membership']['receivers'],
        'any_normal_memberships': request.session['gift_membership']['any_normal_memberships']
    }
    return render(request, 'central/enrollment/gift/receipt.html', context)

def clear(request):
    del request.session['gift_membership']
    return redirect('enrollment.gift.views.index')
