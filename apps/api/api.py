import json

from django.http import HttpResponse

from user.models import User
from focus.models import Actor
from exceptions import BadRequest
from util import get_member_data, get_forening_data, require_focus
import error_codes

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
                except (Actor.DoesNotExist, ValueError):
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
        # TODO
        pass
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
                    except (Actor.DoesNotExist, ValueError):
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
