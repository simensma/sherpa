# encoding: utf-8
from django.template.loader import render_to_string
from django.template import RequestContext
from django.http import HttpResponse
from django.core.cache import cache
from django.conf import settings

from urllib import quote_plus
import requests
import re
import logging
import sys
import json

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

def send_sms_receipt(request, user):
    number = re.sub('\s', '', user.get_phone_mobile())
    try:
        context = RequestContext(request, {
            'mob_user': user,
            'all_paid': all(u.has_paid() for u in [user] + list(user.get_children()))
        })
        sms_message = render_to_string('main/membership/memberid_sms/message.txt', context).encode('utf-8')
        r = requests.get(settings.SMS_URL % (quote_plus(number), quote_plus(sms_message)))
        if r.text.find("1 SMS messages added to queue") == -1:
            logger.error(u"Kunne ikke sende medlemsnummer på SMS: Ukjent status",
                exc_info=sys.exc_info(),
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

