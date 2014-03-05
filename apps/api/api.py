from django.http import HttpResponse

import json

from user.models import User
from focus.models import Actor
from exceptions import BadRequest
from util import get_member_data, require_focus
import error_codes

def members(request, version, format):
    if request.method == 'GET':
        require_focus()

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
                "A member matching that sherpa_id, memberid, or both if both were provided, does not exist.",
                code=error_codes.RESOURCE_NOT_FOUND,
                http_code=404
            )
    else:
        raise BadRequest(
            "Unsupported HTTP verb",
            code=error_codes.UNSUPPORTED_HTTP_VERB,
            http_code=400
        )
