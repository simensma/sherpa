# encoding: utf-8
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.core.cache import cache
from django.conf import settings

from sherpa.decorators import user_requires_login
from sherpa2.models import Association
from focus.models import FocusZipcode, Price, Actor
from focus.util import ACTOR_ENDCODE_DUBLETT
from core.models import Zipcode
from enrollment.models import State
from enrollment.gift.models import membership_price_by_code
from membership.models import SMSServiceRequest
from user.models import User
from membership.util import send_sms_receipt, memberid_sms_count

import json
import logging
import sys
import re

logger = logging.getLogger('sherpa')

def index(request):
    context = {'gift_membership_prices': membership_price_by_code}
    return render(request, 'main/membership/index.html', context)

def benefits(request, association_id):
    if association_id is None:
        # No association-attachment provided, use default prices (DNT Oslo og Omegn).
        association_focus_id = 10
        association = None
    else:
        association = cache.get('association_sherpa2.%s' % association_id)
        if association is None:
            association = Association.objects.get(id=association_id)
            cache.set('association_sherpa2.%s' % association_id, association, 60 * 60 * 24 * 7)
        association_focus_id = association.focus_id

    price = cache.get('association.price.%s' % association_focus_id)
    if price is None:
        price = Price.objects.get(association_id=association_focus_id)
        cache.set('association.price.%s' % association_focus_id, price, 60 * 60 * 24 * 7)

    context = {
        'association': association,
        'price': price,
        'enrollment_active': State.objects.all()[0].active,
    }
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
        association = cache.get('association_sherpa2.focus.%s' % focus_association_id)
        if association is None:
            association = Association.objects.get(focus_id=focus_association_id)
            cache.set('association_sherpa2.focus.%s' % focus_association_id, association, 60 * 60 * 24 * 7)

        # Success, redirect user
        url = "%s-%s/" % (reverse('membership.views.benefits', args=[association.id])[:-1], slugify(association.name))
        return HttpResponse(json.dumps({'url': url}))

    except FocusZipcode.DoesNotExist:
        # The Zipcode doesn't exist in Focus, but if it exists in our Zipcode model, Focus is just not updated
        if Zipcode.objects.filter(zipcode=request.POST['zipcode']).exists():
            logger.warning(u"Postnummer finnes i Zipcode, men ikke i Focus!",
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
        logger.warning(u"Focus-postnummer mangler foreningstilknytning!",
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

    # Robots etc, just redirect them
    if not 'phone_mobile' in request.POST:
        return redirect('membership.views.service')

    # Start recording this request - details will be filled underway
    sms_request = SMSServiceRequest()
    sms_request.phone_number_input = request.POST['phone_mobile']
    sms_request.ip = request.META['REMOTE_ADDR']
    if request.user.is_authenticated():
        sms_request.user = request.user

    sms_request.count = memberid_sms_count(request.META['REMOTE_ADDR'])
    if sms_request.count > 10 and request.META['REMOTE_ADDR'] not in settings.SMS_RESTRICTION_WHITELIST:
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
    elif len(actors) == 1:
        actor = actors[0]
    elif len(actors) > 1:
        # Usually, this will be because children have the same number as their parents.
        # Check if any of these are related, and in that case, use the parent.
        actor = None
        for actor_to_check in actors:
            if actor_to_check.get_parent_memberid() is not None:
                parent = Actor.objects.get(memberid=actor_to_check.get_parent_memberid())
                if parent in actors:
                    # Ah, this parent is in the result set - probably the one we want, use it
                    actor = parent
                    break
        if actor is None:
            # Multiple hits, and they are not related. What do? Pick a random hit for now.
            actor = actors[0]
    else:
        raise Exception("A negative number of actors resulted from raw query. This is very strange, please investigate immediately.")
    user = User.get_or_create_inactive(memberid=actor.memberid)
    sms_request.memberid = user.memberid
    sms_request.save()
    return send_sms_receipt(request, user)

@user_requires_login()
def memberid_sms_userpage(request):
    # Requests from the userpage
    user = request.user

    sms_request = SMSServiceRequest(
        phone_number_input=None,
        ip=request.META['REMOTE_ADDR'],
        user=request.user,
        memberid=user.memberid
    )

    sms_request.count = memberid_sms_count(request.META['REMOTE_ADDR'])
    if sms_request.count > 10:
        sms_request.blocked = True
        sms_request.save()
        return HttpResponse(json.dumps({'status': 'too_high_frequency'}))

    if user.get_phone_mobile() == '':
        # This shouldn't happen (it's checked client-side first) - but handle it anyway, just in case
        return HttpResponse(json.dumps({
            'status': 'missing_number'
        }))
    sms_request.save()
    return send_sms_receipt(request, user)
