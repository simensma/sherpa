# encoding: utf-8
from django.shortcuts import render
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.core.cache import cache
from django.conf import settings
from django.template import RequestContext
from django.template.loader import render_to_string

from sherpa2.models import Association
from focus.models import FocusZipcode, Price, Actor, ACTOR_ENDCODE_DUBLETT
from core.models import Zipcode
from enrollment.models import State
from membership.models import SMSServiceRequest

from datetime import datetime, timedelta
import json
import logging
import sys
import re
import requests
from urllib import quote_plus

logger = logging.getLogger('sherpa')

def index(request):
    return render(request, 'main/membership/index.html')

def benefits(request, association_id):
    if association_id is None:
        # No association-attachment provided, use default prices (DNT Oslo og Omegn).
        association_focus_id = 10
        association = None
    else:
        association = cache.get('association.%s' % association_id)
        if association is None:
            association = Association.objects.get(id=association_id)
            cache.set('association.%s' % association_id, association, 60 * 60 * 24)
        association_focus_id = association.focus_id

    price = cache.get('association.price.%s' % association_focus_id)
    if price is None:
        price = Price.objects.get(association_id=association_focus_id)
        cache.set('association.price.%s' % association_focus_id, price, 60 * 60 * 24 * 7)

    now = datetime.now()
    new_membership_year = datetime(year=now.year, month=settings.MEMBERSHIP_YEAR_START, day=now.day)

    context = {
        'association': association,
        'price': price,
        'now': now,
        'enrollment_active': State.objects.all()[0].active,
        'new_membership_year': new_membership_year}
    return render(request, 'main/membership/benefits.html', context)

def zipcode_search(request):
    if not 'zipcode' in request.POST:
        return HttpResponse(json.dumps({'error': 'missing_zipcode'}))

    try:
        # Get focus zipcode-association ID
        focus_association_id = cache.get('focus.zipcode_association.%s' % request.POST['zipcode'])
        if focus_association_id is None:
            focus_association_id = FocusZipcode.objects.get(zipcode=request.POST['zipcode']).main_association_id
            cache.set('focus.zipcode_association.%s' % request.POST['zipcode'], focus_association_id, 60 * 60 * 24 * 7)

        # Get association based on zipcode-ID
        association = cache.get('focus.association.%s' % focus_association_id)
        if association is None:
            association = Association.objects.get(focus_id=focus_association_id)
            cache.set('focus.association.%s' % focus_association_id, association, 60 * 60 * 24 * 7)

        # Success, redirect user
        url = "%s-%s/" % (reverse('membership.views.benefits', args=[association.id])[:-1], slugify(association.name))
        return HttpResponse(json.dumps({'url': url}))

    except FocusZipcode.DoesNotExist:
        # The Zipcode doesn't exist in Focus, but if it exists in our Zipcode model, Focus is just not updated
        if Zipcode.objects.filter(zipcode=request.POST['zipcode']).exists():
            logger.error(u"Postnummer finnes i Zipcode, men ikke i Focus!",
                exc_info=sys.exc_info(),
                extra={
                    'request': request,
                    'postnummer': request.POST['zipcode']
                }
            )
            return HttpResponse(json.dumps({'error': 'unregistered_zipcode', 'zipcode': request.POST['zipcode']}))
        else:
            # This *could* be an entirely new Zipcode, or just an invalid one.
            return HttpResponse(json.dumps({'error': 'invalid_zipcode', 'zipcode': request.POST['zipcode']}))

    except Association.DoesNotExist:
        logger.error(u"Focus-postnummer mangler foreningstilknytning!",
            exc_info=sys.exc_info(),
            extra={'request': request}
        )
        return HttpResponse(json.dumps({'error': 'unregistered_zipcode', 'zipcode': request.POST['zipcode']}))

def service(request):
    return render(request, 'main/membership/service.html')

def memberid_sms(request):
    # This is a membership service that lets you get your memberid by providing your phone number.
    # Note that a lot of phone number entries in Focus are bogus (email, date of birth, or
    # poorly formatted) and some are also foreign, which we allow for now.
    # We are currently relying on the SMS service to fail if a bogus number
    # happens to fall through.

    # Use the local cache to count requests, identify on IP
    def memberid_sms_count(ip_address):
        lookups = cache.get('memberid_sms_requests.%s' % ip_address)
        if lookups is None:
            lookups = 1
        else:
            lookups += 1
        cache.set('memberid_sms_requests.%s' % ip_address, lookups, 60 * 30)
        return lookups

    # Start recording this request - details will be filled underway
    sms_request = SMSServiceRequest()
    sms_request.phone_number_input = request.POST['phone_mobile']
    sms_request.ip = request.META['REMOTE_ADDR']
    if request.user.is_authenticated():
        sms_request.profile = request.user.get_profile()

    # Simple security - if the same person (IP) sends > 10 requests within 30 minutes,
    # we'll suspect something's up.
    sms_request.count = memberid_sms_count(request.META['REMOTE_ADDR'])
    if sms_request.count > 10:
        sms_request.blocked = True
        sms_request.save()
        return HttpResponse(json.dumps({'status': 'too_high_frequency'}))

    number = re.sub('\s', '', request.POST['phone_mobile'])
    if number == '':
        sms_request.save()
        return HttpResponse(json.dumps({'status': 'no_match'}))
    # Note that we're excluding Actors with end_code 'dublett' manually here
    actors = Actor.objects.raw(
        "select * from Actor where REPLACE(MobPh, ' ', '') = %s AND EndCd != %s;", [number, ACTOR_ENDCODE_DUBLETT])
    actors = list(actors) # Make sure the query has been performed
    if len(actors) == 0:
        sms_request.save()
        return HttpResponse(json.dumps({'status': 'no_match'}))
    elif len(actors) > 1:
        # TODO: More than one hits, ignore for now - what should we do here?
        pass
    actor = actors[0]
    sms_request.memberid = actor.memberid
    sms_request.save()

    try:
        context = RequestContext(request, {
            'actor': actor,
            'year': datetime.now().year,
            'next_year': datetime.now().month >= settings.MEMBERSHIP_YEAR_START,
            'all_payed': all(a.has_payed() for a in [actor] + list(actor.get_children()))
        })
        sms_message = render_to_string('main/membership/memberid_sms.txt', context).encode('utf-8')
        r = requests.get(settings.SMS_URL % (quote_plus(number), quote_plus(sms_message)))
        status = re.findall('Status: .*', r.text)
        if len(status) == 0 or status[0][8:] != 'Meldingen er sendt':
            logger.error(u"Kunne ikke sende medlemsnummer på SMS: Ukjent status",
                exc_info=sys.exc_info(),
                extra={
                    'request': request,
                    'number': number,
                    'response_status': r.text,
                    'sms_response_object': r
                }
            )
            return HttpResponse(json.dumps({
                'status': 'service_fail'}
            ))
        return HttpResponse(json.dumps({'status': 'ok'}))
    except requests.ConnectionError:
        logger.error(u"Kunne ikke sende medlemsnummer på SMS: requests.ConnectionError",
            exc_info=sys.exc_info(),
            extra={
                'request': request,
                'number': number
            }
        )
        return HttpResponse(json.dumps({
            'status': 'connection_error'}
        ))
