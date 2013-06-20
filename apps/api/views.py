# encoding: utf-8
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from exceptions import BadRequest
import api

supported_formats = ['json', 'xml']
versions = ['1']

@csrf_exempt
def index(request, object):
    try:
        version, format = get_requested_representation(request)
        if object == 'members':
            return api.members(request, version, format)
        raise Http404
    except BadRequest as e:
        return HttpResponseBadRequest(e.message)

# Not a view
def get_requested_representation(request):
    version = request.GET.get('version', versions[len(versions) - 1])
    if not version in versions:
        raise BadRequest("The provided API version '%s' is not one of the following supported versions: %s" % (version, ', '.join(versions)))

    format = request.GET.get('format', supported_formats[0])
    if not format in supported_formats:
        raise BadRequest("The requested representation format '%s' is not one of the following supported formats: %s" % (format, ', '.join(supported_formats)))

    return version, format
