from analytics.models import Visitor, Request, Pageview
from datetime import datetime

class Analytics():
    def process_request(self, request):
        # Don't process requests to static files
        statics = ['favicon.ico', 'robots.txt']
        if request.path[1:] in statics:
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
          url=request.path,
          server_host=request.get_host(),
          client_ip=request.META['REMOTE_ADDR'],
          client_host=request.META.get('REMOTE_HOST'),
          referrer=request.META.get('HTTP_REFERER'),
          enter=datetime.now())
        requestObject.save()

        request.session['request'] = requestObject
        return None

    def process_response(self, request, response):
        if 'request' in request.session:
            del request.session['request']
        return response
