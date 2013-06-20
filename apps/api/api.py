from django.http import HttpResponse

import json

from user.models import Profile
from exceptions import BadRequest
from util import get_member_data

def members(request, version, format):
    if request.method == 'GET':
        try:
            if 'sherpa_id' in request.GET and 'medlemsnummer' in request.GET:
                profile = Profile.objects.get(id=request.GET['sherpa_id'], memberid=request.GET['medlemsnummer'])
            elif 'sherpa_id' in request.GET:
                profile = Profile.objects.get(id=request.GET['sherpa_id'])
            elif 'medlemsnummer' in request.GET:
                # TODO: Create inactive profile if the memberid matches an Actor
                profile = Profile.objects.get(memberid=request.GET['medlemsnummer'])
            else:
                raise BadRequest("You must supply either an 'sherpa_id' or 'medlemsnummer' parameter for member lookup")
            return HttpResponse(json.dumps(get_member_data(profile)))
        except Profile.DoesNotExist:
            return HttpResponse('does not exist, what should i do?')
    else:
        raise BadRequest("Unsupported HTTP verb")
