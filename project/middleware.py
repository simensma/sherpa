from analytics.models import Visitor, Request, Parameter, Pageview
from django.conf import settings
from datetime import datetime

class Analytics():
    def process_request(self, request):
        # Don't process requests to static files
        statics = ['/favicon.ico', '/robots.txt']
        if request.path in statics or request.path.startswith(settings.STATIC_URL):
            return None

        # Store new visitor sessions
        if not 'visitor' in request.session:
            if request.user.is_authenticated():
                # Logged-in user without a visitor in session.
                # In theory, this should never happen.
                visitor = request.user.get_profile().visitor
                request.session['visitor'] = visitor.id
            else:
                # Completely new user
                visitor = Visitor()
                visitor.save()
                request.session['visitor'] = visitor.id
        else:
            visitor = Visitor.objects.get(id=request.session['visitor'])

        requestObject = Request(
          visitor=visitor,
          http_method=request.method,
          path=request.path,
          server_host=request.get_host(),
          client_ip=request.META.get('REMOTE_ADDR', ''),
          client_host=request.META.get('REMOTE_HOST', ''),
          referrer=request.META.get('HTTP_REFERER', ''),
          enter=datetime.now(),
          ajax=request.is_ajax())
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
