# encoding: utf-8
import json
import hmac
import hashlib

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from focus.models import Actor, Enrollment
from foreninger.models import Forening, Supply
from turbasen.models import Sted
from user.models import User, CabinVisit, CabinVisitor

@csrf_exempt
def create_transaction(request):
    """This view is called by the phone app to initiate a new transaction"""
    if request.method == 'OPTIONS':
        # Handle CORS preflight
        request_headers = request.META.get('HTTP_ACCESS_CONTROL_REQUEST_HEADERS')
        response = HttpResponse()
        if request_headers is not None:
            response['Access-Control-Allow-Headers'] = request_headers
        response['Access-Control-Allow-Method'] = 'POST'
        return response

    transaction = json.loads(request.POST['data'])

    sted = Sted.get(transaction['hytte'])
    # TODO: Handle cabins with multiple owners (defaulting to first occurrence for now)
    forening = Forening.objects.get(turbase_object_id=sted.grupper[0])

    cabin_visit = CabinVisit(
        order_number=CabinVisit.generate_order_number(),
    )
    cabin_visit.save()

    amount = 0
    for gjest in transaction['gjester']:
        cabin_visitor = CabinVisitor(
            cabin_visit=cabin_visit,
            protocol_number=gjest['protokollnummer'],
        )
        cabin_visitor.save()

        if gjest['medlemsnummer'] is None:
            is_member = False
        else:
            try:
                user = User.get_or_create_inactive(memberid=gjest['medlemsnummer'], include_pending=True)
                if not user.has_paid():
                    # TODO: confirm in the client that one or more users aren't valid
                    raise NotImplementedError
                is_member = True

                cabin_visitor.user = user
                cabin_visitor.save()
            except (Actor.DoesNotExist, Enrollment.DoesNotExist):
                # TODO: handle invalid memberid
                raise NotImplementedError

        for losji in gjest['losji']:
            lodging = forening.lodging_prices.get(id=losji['id'])
            if is_member:
                amount += lodging.price_member * losji['antall']
            else:
                amount += lodging.price_nonmember * losji['antall']

        for proviant in gjest["proviant"]:
            supply = Supply.objects.get(
                id=proviant['id'],
                supply_category__forening=forening.id,
            )
            if is_member:
                amount += supply.price_member * proviant['antall']
            else:
                amount += supply.price_nonmember * proviant['antall']

    # The price to DIBS is provided in øre
    amount *= 100

    accept_return_url = u'https://dnt-backend.herokuapp.com/' # TODO implement

    callback_url = u'https://%s%s' % (
        request.site.domain,
        reverse('payment.views.callback_endpoint')
    )

    input_parameters = {
        u'acceptReturnUrl': accept_return_url,
        u'amount': amount,
        u'callbackUrl': callback_url,
        u'currency': u'NOK', # ISO 4217
        u'merchant': settings.DIBS_MERCHANT_ID,
        u'test': 1, # Temporary; triggers test-environment at DIBS
    }

    sorted_pairs = sorted(input_parameters.items(), key=lambda i: i[0])
    sorted_string = [u"%s=%s" % (i[0], i[1]) for i in sorted_pairs]
    message = u'&'.join(sorted_string).encode('utf-8')

    MAC = hmac.new(settings.DIBS_HMAC_KEY.decode('hex'), message, hashlib.sha256).hexdigest()

    return HttpResponse(json.dumps({
        'MAC': MAC,
        'ticket': None, # TODO: if authenticated, return user's DIBS ticket
        'callbackUrl': callback_url,
        'orderId': cabin_visit.order_number,
        'acceptReturnUrl': accept_return_url,
    }))

def callback_endpoint(request):
    raise NotImplementedError
