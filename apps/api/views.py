# encoding: utf-8
from django.http import Http404, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from exceptions import BadRequest
from util import get_requested_representation, authenticate
import api

@csrf_exempt
def index(request, resource):
    try:
        if not authenticate(request):
            raise BadRequest("Ugyldig autentiseringsnøkkel")
        version, format = get_requested_representation(request)
        if resource == 'members':
            return api.members(request, version, format)
        raise Exception("Invalid URL resource specified: %s" % resource)
    except BadRequest as e:
        return HttpResponseBadRequest(e.message)
