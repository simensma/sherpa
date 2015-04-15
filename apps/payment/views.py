# encoding: utf-8
import json
import hmac
import hashlib

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from .products import cabin_visit

@csrf_exempt
def create_transaction(request):
    """This view is called by the phone app to initiate a new transaction"""
    if request.method != 'POST' or 'data' not in request.POST:
        raise PermissionDenied

    transaction = json.loads(request.POST['data'])
    product = transaction.get('product', '')

    if product == 'cabin_visit':
        amount, order_number = cabin_visit(transaction)
    else:
        return HttpResponseBadRequest("Unknown product '%s'" % product)

    # The price to DIBS is provided in øre
    amount *= 100

    accept_return_url = reverse('payment.views.postmessage_callback')

    callback_url = u'https://%s%s' % (
        request.site.domain,
        reverse('payment.views.payment_provider_callback')
    )

    input_parameters = {
        u'acceptReturnUrl': accept_return_url,
        u'amount': amount,
        u'callbackUrl': callback_url,
        u'currency': u'NOK', # ISO 4217
        u'merchant': settings.DIBS_MERCHANT_ID,
        u'orderId': order_number,
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
        'orderId': order_number,
        'acceptReturnUrl': accept_return_url,
        'amount': amount,
    }))

def postmessage_callback(request):
    """Render an empty page with a postMessage to the parent window, letting them know the frame has completed items
    transaction work"""
    return render(request, 'central/payment/postmessage.html')

def payment_provider_callback(request):
    raise NotImplementedError
