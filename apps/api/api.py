# encoding: utf-8
from datetime import datetime
import json
import logging
import sys

from django.http import HttpResponse
from django.core.cache import cache

from core.models import Zipcode
from user.models import User
from foreninger.models import Forening
from focus.models import Enrollment, FocusZipcode, Price
from focus.util import get_membership_type_by_codename
from exceptions import BadRequest
from util import get_member_data, get_forening_data, require_focus
import error_codes

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
                    "You must supply either an 'sherpa_id' or 'medlemsnummer' parameter for member lookup",
                    code=error_codes.MISSING_REQUIRED_PARAMETER,
                    http_code=400
                )
            return HttpResponse(json.dumps(get_member_data(user)))
        except (User.DoesNotExist, ValueError):
            raise BadRequest(
                "A member matching that 'sherpa_id', 'medlemsnummer', or both if both were provided, does not exist.",
                code=error_codes.RESOURCE_NOT_FOUND,
                http_code=404
            )
    else:
        raise BadRequest(
            "Unsupported HTTP verb",
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
                "Could not parse the 'født' parameter ('%s'), which should be in the following format: 'dd.mm.yyyy'" %
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
                    user_data = {
                        'hovedmedlem': get_member_data(user.get_parent()),
                        'husstandsmedlemmer': [get_member_data(u) for u in user.get_parent().get_children()],
                    }
            else:
                user_data = get_member_data(user)

            return HttpResponse(json.dumps(user_data))
        except (User.DoesNotExist, ValueError):
            raise BadRequest(
                "A membership with member ID '%s' and date of birth '%s' does not exist." %
                    (request.GET['medlemsnummer'], request.GET[u'født']),
                code=error_codes.RESOURCE_NOT_FOUND,
                http_code=404
            )

    else:
        raise BadRequest(
            "Unsupported HTTP verb",
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
                    "The postal code '%s' exists, but isn't connected to a Forening. It should be, and we've logged this occurrence." %
                        request.GET['postnummer'],
                    code=error_codes.RESOURCE_NOT_FOUND,
                    http_code=404
                )
            else:
                # This *could* be an entirely new Zipcode, or just an invalid one.
                raise BadRequest(
                    "The postal code '%s' isn't registered in our database." %
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
                "The postal code '%s' exists, but isn't connected to a Forening. It should be, and we've logged this occurrence." %
                    request.GET['postnummer'],
                code=error_codes.RESOURCE_NOT_FOUND,
                http_code=404
            )

    else:
        raise BadRequest(
            "Unsupported HTTP verb",
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
                    "A member matching that 'sherpa_id', 'bruker_medlemsnummer', or both if both were provided, does not exist.",
                    code=error_codes.RESOURCE_NOT_FOUND,
                    http_code=404
                )
        else:
            raise BadRequest(
                "You must supply either a 'bruker_sherpa_id' or 'bruker_medlemsnummer' parameter for forening lookup by member. Only this form of forening-lookup is implemented in this version.",
                code=error_codes.MISSING_REQUIRED_PARAMETER,
                http_code=400
            )
    else:
        raise BadRequest(
            "Unsupported HTTP verb",
            code=error_codes.UNSUPPORTED_HTTP_VERB,
            http_code=400
        )
