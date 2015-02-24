# encoding: utf-8
import json

from django.core.urlresolvers import reverse
from django.http import HttpResponse

from focus.models import Actor, Enrollment
from foreninger.models import Forening, Supply
from turbasen.models import Sted
from user.models import User

def create_transaction(request):
    """This view is called by the phone app to initiate a new transaction"""
    transaction = json.loads(request.POST['data'])

    sted = Sted.get(transaction['hytte'])
    # TODO: Handle cabins with multiple owners (defaulting to first occurrence for now)
    forening = Forening.objects.get(turbase_object_id=sted.grupper[0])

    amount = 0
    for gjest in transaction['gjester']:
        if gjest['medlemsnummer'] is None:
            is_member = False
        else:
            try:
                user = User.get_or_create_inactive(memberid=gjest['medlemsnummer'], include_pending=True)
                if not user.has_paid():
                    # TODO: confirm in the client that one or more users aren't valid
                    raise NotImplementedError
                is_member = True
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

    return HttpResponse(json.dumps({
        'MAC': None,
        'ticket': None,
        'callbackUrl': 'https://%s%s' % (
            request.site.domain,
            reverse('payment.views.callback_endpoint')
        ),
        'orderId': None,
    }))

def callback_endpoint(request):
    raise NotImplementedError
