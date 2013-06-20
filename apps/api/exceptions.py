from django.http import HttpResponse

import json

# We'd like to use BadRequest like Django's PermissionDenied exception here
class BadRequest(Exception):
    def __init__(self, message, code, http_code):
        self.message = message
        self.code = code
        self.http_code = http_code

    def response(self):
        return HttpResponse(json.dumps({
            'errors': [{
                'message': self.message,
                'code': self.code,
            }]
        }), status=self.http_code)
