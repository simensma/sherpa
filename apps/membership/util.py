# encoding: utf-8
from urllib import quote_plus
import re
import logging
import sys

from django.template.loader import render_to_string
from django.template import RequestContext
from django.core.cache import cache
from django.conf import settings

import requests

from focus.models import Actor
from focus.util import ACTOR_ENDCODE_DUBLETT
from user.models import User

logger = logging.getLogger('sherpa')

# Simple security - if the same person (IP) sends > 10 requests within 30 minutes,
# we'll suspect something's up.
# Use the local cache to count requests, identify on IP
def memberid_sms_count(ip_address):
    lookups = cache.get('memberid_sms_requests.%s' % ip_address)
    if lookups is None:
        lookups = 1
    else:
        lookups += 1
    cache.set('memberid_sms_requests.%s' % ip_address, lookups, 60 * 30)
    return lookups

def lookup_users_by_phone(phone_number):
    """Attempt to match the given phone number in an arbitrary format to one or more members"""
    phone_number = re.sub('\s', '', phone_number)
    if phone_number == '':
        return []

    # Note that we're excluding Actors with end_code 'dublett' manually here
    actors = Actor.objects.raw(
        "select * from Actor where REPLACE(MobPh, ' ', '') = %s AND EndCd != %s;",
        [phone_number, ACTOR_ENDCODE_DUBLETT]
    )

    # Convert the matching actors to users. Filter on personal members; we're never handling other membership types
    return [User.get_or_create_inactive(memberid=actor.memberid) for actor in actors if actor.is_personal_member()]

def send_sms_receipt(request, user):
    """Send an SMS receipt for membership to the given user. Note that if the user has children, their status will
    also be included. However, if this is a household member, we'll send the receipt to the member without further
    information about the related and/or parent members."""
    number = user.get_phone_mobile(strip_whitespace=True)
    try:
        context = RequestContext(request, {
            'mob_user': user,
            'all_paid': all(u.has_paid() for u in [user] + list(user.get_children()))
        })
        sms_message = render_to_string('central/membership/memberid_sms/message.txt', context).encode('utf-8')
        r = requests.get(settings.SMS_URL % (quote_plus(number), quote_plus(sms_message)))
        if r.text.find("1 SMS messages added to queue") == -1:
            logger.error(u"Kunne ikke sende medlemsnummer på SMS: Ukjent status",
                extra={
                    'request': request,
                    'number': number,
                    'response_text': r.text,
                    'sms_request_object': r
                }
            )
            return {'status': 'service_fail'}
        return {'status': 'ok'}
    except requests.ConnectionError:
        logger.error(u"Kunne ikke sende medlemsnummer på SMS: requests.ConnectionError",
            exc_info=sys.exc_info(),
            extra={
                'request': request,
                'number': number
            }
        )
        return {'status': 'connection_error'}
