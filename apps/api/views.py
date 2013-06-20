# encoding: utf-8
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from exceptions import BadRequest
from util import get_requested_representation
import api

@csrf_exempt
def index(request, object):
    try:
        version, format = get_requested_representation(request)
        if object == 'members':
            return api.members(request, version, format)
        raise Http404
    except BadRequest as e:
        return HttpResponseBadRequest(e.message)
