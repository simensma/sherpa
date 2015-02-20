# encoding: utf-8
from datetime import datetime
import json
import logging
import sys

from django.http import HttpResponse
from django.core.cache import cache

from . import error_codes
from .exceptions import BadRequest
from core.models import Zipcode
from focus.models import Enrollment, FocusZipcode, Price
from focus.util import get_membership_type_by_codename
from foreninger.models import Forening
from membership.util import lookup_users_by_phone, send_sms_receipt
from user.models import User
from util import get_member_data, get_forening_data, require_focus

logger = logging.getLogger('sherpa')

def members(request, version, format):
    if request.method == 'GET':
        require_focus(request)

        try:
            if 'sherpa_id' in request.GET and 'medlemsnummer' in request.GET:
                user = User.get_users(include_pending=True).get(id=request.GET['sherpa_id'], memberid=request.GET['medlemsnummer'])
            elif 'sherpa_id' in request.GET:
                user = User.get_users(include_pending=True).get(id=request.GET['sherpa_id'])
            elif 'medlemsnummer' in request.GET:
                try:
                    user = User.get_or_create_inactive(memberid=request.GET['medlemsnummer'], include_pending=True)
                except (Enrollment.DoesNotExist, ValueError):
                    # No such member
                    raise User.DoesNotExist
            else:
                raise BadRequest(
                    u"You must supply either an 'sherpa_id' or 'medlemsnummer' parameter for member lookup",
                    code=error_codes.MISSING_REQUIRED_PARAMETER,
                    http_code=400
                )
            return HttpResponse(json.dumps(get_member_data(user)))
        except (User.DoesNotExist, ValueError):
            raise BadRequest(
                u"A member matching that 'sherpa_id', 'medlemsnummer', or both if both were provided, does not exist.",
                code=error_codes.RESOURCE_NOT_FOUND,
                http_code=404
            )
    else:
        raise BadRequest(
            u"Unsupported HTTP verb",
            code=error_codes.UNSUPPORTED_HTTP_VERB,
            http_code=400
        )

def membership(request, version, format):
    if request.method == 'GET':
        require_focus(request)

        if not 'medlemsnummer' in request.GET or not u'født' in request.GET:
            raise BadRequest(
                u"Missing 'medlemsnummer' and/or 'født' parameters'",
                code=error_codes.MISSING_REQUIRED_PARAMETER,
                http_code=400
            )

        try:
            requested_date_of_birth = datetime.strptime(request.GET[u'født'], "%d.%m.%Y").date()
        except ValueError:
            raise BadRequest(
                u"Could not parse the 'født' parameter ('%s'), which should be in the following format: 'dd.mm.yyyy'" %
                    request.GET[u'født'],
                code=error_codes.MISSING_REQUIRED_PARAMETER,
                http_code=400
            )

        try:
            try:
                user = User.get_or_create_inactive(memberid=request.GET['medlemsnummer'], include_pending=True)
            except (Enrollment.DoesNotExist, ValueError):
                # No such member
                raise User.DoesNotExist

            # Verify the requested date of birth
            if user.get_birth_date() != requested_date_of_birth:
                raise User.DoesNotExist

            if 'hele_husstanden' in request.GET:
                if not user.is_household_member():
                    user_data = {
                        'hovedmedlem': get_member_data(user),
                        'husstandsmedlemmer': [get_member_data(u) for u in user.get_children()],
                    }
                else:
                    if user.get_parent() is not None:
                        user_data = {
                            'hovedmedlem': get_member_data(user.get_parent()),
                            'husstandsmedlemmer': [get_member_data(u) for u in user.get_parent().get_children()],
                        }
                    else:
                        # A household member without a parent, send it as such
                        user_data = {
                            'hovedmedlem': None,
                            'husstandsmedlemmer': [get_member_data(user)],
                        }
            else:
                user_data = get_member_data(user)

            return HttpResponse(json.dumps(user_data))
        except (User.DoesNotExist, ValueError):
            raise BadRequest(
                u"A membership with member ID '%s' and date of birth '%s' does not exist." %
                    (request.GET['medlemsnummer'], request.GET[u'født']),
                code=error_codes.RESOURCE_NOT_FOUND,
                http_code=404
            )

    else:
        raise BadRequest(
            u"Unsupported HTTP verb",
            code=error_codes.UNSUPPORTED_HTTP_VERB,
            http_code=400
        )

def membership_price(request, version, format):
    if request.method == 'GET':
        require_focus(request)

        if not 'postnummer' in request.GET:
            raise BadRequest(
                u"Missing required 'postnummer' parameter",
                code=error_codes.MISSING_REQUIRED_PARAMETER,
                http_code=400
            )

        try:
            # Get focus zipcode-forening ID
            focus_forening_id = cache.get('focus.zipcode_forening.%s' % request.GET['postnummer'])
            if focus_forening_id is None:
                focus_forening_id = FocusZipcode.objects.get(zipcode=request.GET['postnummer']).main_forening_id
                cache.set('focus.zipcode_forening.%s' % request.GET['postnummer'], focus_forening_id, 60 * 60 * 24 * 7)

            # Get forening based on zipcode-ID
            forening = Forening.objects.get(focus_id=focus_forening_id)
            price = Price.objects.get(forening_id=forening.focus_id)

            # Success, return the appropriate data
            return HttpResponse(json.dumps({
                'forening': {'sherpa_id': forening.id, 'navn': forening.name},
                'pristabell': {
                    'main': {
                        'navn': get_membership_type_by_codename('main')['name'],
                        'pris': price.main,
                    },
                    'youth': {
                        'navn': get_membership_type_by_codename('youth')['name'],
                        'pris': price.youth,
                    },
                    'senior': {
                        'navn': get_membership_type_by_codename('senior')['name'],
                        'pris': price.senior,
                    },
                    'lifelong': {
                        'navn': get_membership_type_by_codename('lifelong')['name'],
                        'pris': price.lifelong,
                    },
                    'child': {
                        'navn': get_membership_type_by_codename('child')['name'],
                        'pris': price.child,
                    },
                    'school': {
                        'navn': get_membership_type_by_codename('school')['name'],
                        'pris': price.school,
                    },
                    'household': {
                        'navn': get_membership_type_by_codename('household')['name'],
                        'pris': price.household,
                    },
                }
            }))

        except FocusZipcode.DoesNotExist:
            # The Zipcode doesn't exist in Focus, but if it exists in our Zipcode model, Focus is just not updated
            if Zipcode.objects.filter(zipcode=request.GET['postnummer']).exists():
                logger.warning(u"Postnummer finnes i Zipcode, men ikke i Focus!",
                    exc_info=sys.exc_info(),
                    extra={
                        'request': request,
                        'postnummer': request.GET['postnummer']
                    }
                )
                raise BadRequest(
                    u"The postal code '%s' exists, but isn't connected to a Forening. It should be, and we've logged this occurrence." %
                        request.GET['postnummer'],
                    code=error_codes.RESOURCE_NOT_FOUND,
                    http_code=404
                )
            else:
                # This *could* be an entirely new Zipcode, or just an invalid one.
                raise BadRequest(
                    u"The postal code '%s' isn't registered in our database." %
                        request.GET['postnummer'],
                    code=error_codes.RESOURCE_NOT_FOUND,
                    http_code=404
                )

        except Forening.DoesNotExist:
            logger.warning(u"Focus-postnummer mangler foreningstilknytning!",
                exc_info=sys.exc_info(),
                extra={'request': request}
            )
            raise BadRequest(
                u"The postal code '%s' exists, but isn't connected to a Forening. It should be, and we've logged this occurrence." %
                    request.GET['postnummer'],
                code=error_codes.RESOURCE_NOT_FOUND,
                http_code=404
            )

    else:
        raise BadRequest(
            u"Unsupported HTTP verb",
            code=error_codes.UNSUPPORTED_HTTP_VERB,
            http_code=400
        )

def forening(request, version, format):
    if request.method == 'GET':
        require_focus(request)

        if 'bruker_sherpa_id' in request.GET or 'bruker_medlemsnummer' in request.GET:
            try:
                # Lookup by specified members' access
                if 'bruker_sherpa_id' in request.GET and 'bruker_medlemsnummer' in request.GET:
                    user = User.get_users(include_pending=True).get(id=request.GET['bruker_sherpa_id'], memberid=request.GET['bruker_medlemsnummer'])
                elif 'bruker_sherpa_id' in request.GET:
                    user = User.get_users(include_pending=True).get(id=request.GET['bruker_sherpa_id'])
                elif 'bruker_medlemsnummer' in request.GET:
                    try:
                        user = User.get_or_create_inactive(memberid=request.GET['bruker_medlemsnummer'], include_pending=True)
                    except (Enrollment.DoesNotExist, ValueError):
                        # No such member
                        raise User.DoesNotExist

                foreninger = [get_forening_data(f) for f in user.all_foreninger()]
                return HttpResponse(json.dumps(foreninger))

            except (User.DoesNotExist, ValueError):
                raise BadRequest(
                    u"A member matching that 'sherpa_id', 'bruker_medlemsnummer', or both if both were provided, does not exist.",
                    code=error_codes.RESOURCE_NOT_FOUND,
                    http_code=404
                )
        else:
            raise BadRequest(
                u"You must supply either a 'bruker_sherpa_id' or 'bruker_medlemsnummer' parameter for forening lookup by member. Only this form of forening-lookup is implemented in this version.",
                code=error_codes.MISSING_REQUIRED_PARAMETER,
                http_code=400
            )
    else:
        raise BadRequest(
            u"Unsupported HTTP verb",
            code=error_codes.UNSUPPORTED_HTTP_VERB,
            http_code=400
        )

def memberid(request, version, format):
    if request.method != 'GET':
        raise BadRequest(
            u"Unsupported HTTP verb '%s'" % request.method,
            code=error_codes.UNSUPPORTED_HTTP_VERB,
            http_code=400
        )

    require_focus(request)

    if 'mobilnummer' not in request.GET:
        raise BadRequest(
            u"Missing required 'mobilnummer' parameter",
            code=error_codes.MISSING_REQUIRED_PARAMETER,
            http_code=400
        )

    phone_number = request.GET['mobilnummer'].strip()
    users = lookup_users_by_phone(phone_number)

    # Send the recipient an SMS
    if len(users) == 0:
        raise BadRequest(
            u"A member with phone number '%s' wasn't found." % phone_number,
            code=error_codes.RESOURCE_NOT_FOUND,
            http_code=404
        )
    elif len(users) == 1:
        user = users[0]
    elif len(users) > 1:
        # Usually, this will be because household members have the same number as their parents.
        # Check if any of these are related, and in that case, use the parent.
        user = None
        for user_to_check in users:
            if user_to_check.is_household_member() and \
                    user_to_check.get_parent() is not None and \
                    user_to_check.get_parent() in users:
                # Ah, this parent is in the result set - probably the one we want, use it
                user = user_to_check.get_parent()
                break
        if user is None:
            # Multiple hits, and they are not related. What do? Pick a random hit for now.
            user = users[0]

    # Delete the actor cache in case the number was recently updated; the cache may differ from our raw lookup above
    user.get_actor().clear_cache()
    result = send_sms_receipt(request, user)
    if result['status'] == 'ok':
        return HttpResponse(json.dumps({
            'status': 'ok',
            'message': 'An SMS was successfully sent to the member with the given phone number.',
        }))
    elif result['status'] in ['connection_error', 'service_fail']:
        raise BadRequest(
            "There is a problem with our SMS gateway and we were unable to send the SMS.",
            code=error_codes.SMS_GATEWAY_ERROR,
            http_code=500
        )
    else:
        # Might happen if we add a new status code to the send_sms_receipt function and forget to account for it here
        logger.error(u"Unknown SMS return status code '%s'" % result['status'],
            extra={'request': request}
        )
        raise BadRequest(
            "An internal error occurred while trying to send the SMS. This error has been logged and we'll get it fixed asap.",
            code=error_codes.INTERNAL_ERROR,
            http_code=500
        )

def prices(request, version, format):
    if request.method != 'GET':
        raise BadRequest(
            u"Unsupported HTTP verb '%s'" % request.method,
            code=error_codes.UNSUPPORTED_HTTP_VERB,
            http_code=400
        )

    raise NotImplementedError
