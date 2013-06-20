# encoding: utf-8
from django.views.decorators.csrf import csrf_exempt

from exceptions import BadRequest
from util import get_requested_representation, authenticate
import api
import error_codes

@csrf_exempt
def index(request, resource):
    try:
        if not authenticate(request):
            raise BadRequest(
                "Ugyldig autentiseringsnøkkel",
                code=error_codes.INVALID_AUTHENTICATION,
                http_code=403
            )
        version, format = get_requested_representation(request)
        if resource == 'members':
            return api.members(request, version, format)
        raise Exception("Invalid URL resource specified: %s" % resource)
    except BadRequest as e:
        return e.response()
