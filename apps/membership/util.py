# encoding: utf-8
from urllib import quote_plus
import re
import logging
import sys
import json

from django.template.loader import render_to_string
from django.template import RequestContext
from django.http import HttpResponse
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
    # Note also that we're not filtering on Actor.get_personal_members()
    actors = Actor.objects.raw(
        "select * from Actor where REPLACE(MobPh, ' ', '') = %s AND EndCd != %s;",
        [phone_number, ACTOR_ENDCODE_DUBLETT]
    )

    # Convert the matching actors to users
    return [User.get_or_create_inactive(memberid=actor.memberid) for actor in actors]

def send_sms_receipt(request, user):
    number = re.sub('\s', '', user.get_phone_mobile())
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
            return HttpResponse(json.dumps({
                'status': 'service_fail'
            }))
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
            'status': 'connection_error'
        }))

