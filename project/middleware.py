from analytics.models import Visitor

class Analytics():
    def process_request(self, request):
        # If this is a new user, create a new Visitor
        # Todo: Logic around auth
        if not 'visitor' in request.session:
            v = Visitor()
            v.save()
            request.session['visitor'] = v.id

        # Save pageview, events etc
        return None
