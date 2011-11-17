from analytics.models import Visitor, Request, Parameter, Pageview
import settings
from datetime import datetime

class Analytics():
    def process_request(self, request):
        # Don't process requests to static files
        statics = ['/favicon.ico', '/robots.txt']
        if request.path in statics or request.path.startswith(settings.STATIC_URL):
            return None

        # Don't process AJAX requests
        if request.is_ajax():
            return None

        # If this is a new user, create a new Visitor
        # Todo: Logic around auth
        if not 'visitor' in request.session:
            visitor = Visitor()
            visitor.save()
            request.session['visitor'] = visitor.id
        else:
            visitor = Visitor.objects.get(pk=request.session['visitor'])

        requestObject = Request(
          visitor=visitor,
          http_method=request.method,
          path=request.path,
          server_host=request.get_host(),
          client_ip=request.META.get('REMOTE_ADDR', ''),
          client_host=request.META.get('REMOTE_HOST', ''),
          referrer=request.META.get('HTTP_REFERER', ''),
          enter=datetime.now())
        requestObject.save()

        for key, value in request.GET.items():
            p = Parameter(request=requestObject, key=key, value=value)
            p.save()

        request.session['request'] = requestObject
        return None

    def process_response(self, request, response):
        if 'request' in request.session:
            del request.session['request']
        return response
