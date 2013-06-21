# encoding: utf-8
from django.views.decorators.csrf import csrf_exempt

from util import requested_representation_from_header, requested_representation_from_url
from util import authenticate, invalid_authentication_exception, invalid_version_response
from exceptions import BadRequest
import api

@csrf_exempt
def header_versioning(request, versions):
    try:
        if not authenticate(request):
            raise invalid_authentication_exception()
        version, format = requested_representation_from_header(request)
        try:
            resource = [v for v in versions if v['version'] == version][0]['resource']
        except IndexError:
            return invalid_version_response(version)
        return call_api(request, resource, version, format)
    except BadRequest as e:
        return e.response()

@csrf_exempt
def url_versioning(request, resource, version):
    try:
        if not authenticate(request):
            raise invalid_authentication_exception()
        format = requested_representation_from_url(request)
        return call_api(request, resource, version, format)
    except BadRequest as e:
        return e.response()

def call_api(request, resource, version, format):
    if resource == 'members':
        return api.members(request, version, format)
    raise Exception("Invalid URL resource specified: %s" % resource)
