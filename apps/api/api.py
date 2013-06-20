from django.http import HttpResponse

import json

from user.models import Profile
from user.util import create_inactive_user
from focus.models import Actor
from exceptions import BadRequest
from util import get_member_data
import error_codes

def members(request, version, format):
    if request.method == 'GET':
        try:
            if 'sherpa_id' in request.GET and 'medlemsnummer' in request.GET:
                profile = Profile.objects.get(id=request.GET['sherpa_id'], memberid=request.GET['medlemsnummer'])
            elif 'sherpa_id' in request.GET:
                profile = Profile.objects.get(id=request.GET['sherpa_id'])
            elif 'medlemsnummer' in request.GET:
                try:
                    profile = Profile.objects.get(memberid=request.GET['medlemsnummer'])
                except Profile.DoesNotExist as e:
                    try:
                        # Create an inactive profile if the memberid is valid
                        actor = Actor.objects.get(memberid=request.GET['medlemsnummer'])
                        profile = create_inactive_user(actor.memberid)
                    except Actor.DoesNotExist:
                        # Nope, just re-raise the original Profile.DoesNotExist
                        raise e
            else:
                raise BadRequest(
                    "You must supply either an 'sherpa_id' or 'medlemsnummer' parameter for member lookup",
                    code=error_codes.MISSING_REQUIRED_PARAMETER,
                    http_code=400
                )
            return HttpResponse(json.dumps(get_member_data(profile)))
        except Profile.DoesNotExist:
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
