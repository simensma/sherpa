# encoding: utf-8
import json
import logging
import sys

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.core.cache import cache
from django.conf import settings

from sherpa.decorators import user_requires_login
from foreninger.models import Forening
from focus.models import FocusZipcode, Price
from focus.util import DNT_CENTRAL_ID as DNT_CENTRAL_ID_FOCUS
from core.models import Zipcode
from enrollment.models import State
from membership.models import SMSServiceRequest
from membership.util import lookup_users_by_phone, send_sms_receipt, memberid_sms_count

logger = logging.getLogger('sherpa')

def benefits(request, forening_id):
    if forening_id is None:
        # No forening-attachment provided, use default prices; those connected to the DNT central group
        forening = None
        forening_focus_id = DNT_CENTRAL_ID_FOCUS
    else:
        forening = cache.get('forening.%s' % forening_id)
        if forening is None:
            forening = Forening.objects.get(id=forening_id)
            cache.set('forening.%s' % forening_id, forening, 60 * 60 * 24 * 7)
        forening_focus_id = forening.focus_id

    price = cache.get('forening.price.%s' % forening_focus_id)
    if price is None:
        price = Price.objects.get(forening_id=forening_focus_id)
        cache.set('forening.price.%s' % forening_focus_id, price, 60 * 60 * 24 * 7)

    context = {
        'forening': forening,
        'price': price,
        'enrollment_active': State.objects.all()[0].active,
    }
    return render(request, 'central/membership/benefits.html', context)

def zipcode_search(request):
    if not 'zipcode' in request.POST:
        return HttpResponse(json.dumps({'error': 'missing_zipcode'}))

    try:
        # Get focus zipcode-forening ID
        focus_forening_id = cache.get('focus.zipcode_forening.%s' % request.POST['zipcode'])
        if focus_forening_id is None:
            focus_forening_id = FocusZipcode.objects.get(zipcode=request.POST['zipcode']).main_forening_id
            cache.set('focus.zipcode_forening.%s' % request.POST['zipcode'], focus_forening_id, 60 * 60 * 24 * 7)

        # Get forening based on zipcode-ID
        forening = Forening.objects.get(focus_id=focus_forening_id)

        # Success, redirect user
        url = "%s-%s/" % (reverse('membership.views.benefits', args=[forening.id])[:-1], slugify(forening.name))
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

    except Forening.DoesNotExist:
        logger.warning(u"Focus-postnummer mangler foreningstilknytning!",
            exc_info=sys.exc_info(),
            extra={'request': request}
        )
        return HttpResponse(json.dumps({'error': 'unregistered_zipcode', 'zipcode': request.POST['zipcode']}))

def service(request):
    return render(request, 'central/membership/service.html')

def memberid_sms(request):
    """This is a membership service that lets you get your memberid by providing your phone number.
    Note that a lot of phone number entries in Focus are bogus (email, date of birth, or
    poorly formatted) and some are also foreign, which we allow for now.
    We are currently relying on the SMS service to fail if a bogus number
    happens to fall through."""

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

    users = lookup_users_by_phone(request.POST['phone_mobile'])
    if len(users) == 0:
        sms_request.save()
        return HttpResponse(json.dumps({'status': 'no_match'}))
    elif len(users) == 1:
        user = users[0]
    elif len(users) > 1:
        # Usually, this will be because household members have the same number as their parents.
        # Check if any of these are related, and in that case, use the parent.
        user = None
        for user_to_check in users:
            if user_to_check.is_household_member() and user_to_check.get_parent() in users:
                # Ah, this parent is in the result set - probably the one we want, use it
                user = user_to_check.get_parent()
                break
        if user is None:
            # Multiple hits, and they are not related. What do? Pick a random hit for now.
            user = users[0]
    else:
        raise Exception("A negative number of actors resulted from raw query. This is very strange, please investigate immediately.")

    sms_request.memberid = user.memberid
    sms_request.save()

    # Delete the actor cache in case the number was recently updated; the cache may differ from our raw lookup above
    user.get_actor().clear_cache()
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
