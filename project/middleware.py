from analytics.models import Visitor

class Analytics():
    def process_request(self, request):
        # Don't process requests to static files
        statics = ['favicon.ico', 'robots.txt']
        if request.path[1:] in statics:
            return None

        # If this is a new user, create a new Visitor
        # Todo: Logic around auth
        if not 'visitor' in request.session:
            v = Visitor()
            v.save()
            request.session['visitor'] = v.id

        # Save pageview, events etc
        return None
