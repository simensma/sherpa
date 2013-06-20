# encoding: utf-8
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from Crypto.Cipher import AES

from urllib import quote_plus
from datetime import datetime, timedelta
import json
import base64
import time

from core import pkcs7
from api.util import get_member_data

def connect(request, method):
    if not request.GET.get('client', '') in settings.DNT_CONNECT:
        raise PermissionDenied
    else:
        client = settings.DNT_CONNECT[request.GET['client']]

    key = client['shared_secret']
    request_data = json.loads(decrypt(key, request.GET['data']))

    # Check the transmit datestamp
    request_time = datetime.fromtimestamp(request_data['timestamp'])
    if datetime.now() - request_time > timedelta(seconds=settings.DNT_CONNECT_TIMEOUT):
        raise PermissionDenied

    # Redirect to provided url, or the default if none provided
    redirect_url = request.GET['redirect_url'] if request.GET.get('redirect_url') is not None else client['default_redirect_url']

    response_data = {}

    if method == 'bounce':
        response_data['er_autentisert'] = request.user.is_authenticated()

    if request.user.is_authenticated():
        response_data.update(get_member_data(request.user.get_profile()))
    else:
        if method == 'signon':
            request.session['dntconnect'] = {
                'client': client,
                'redirect_url': redirect_url
            }
            return redirect('user.login.views.connect_signon')
        # The only other method is bounce; in which case we'll just send the response as is

    # Append the current timestamp
    response_data['timestamp'] = int(time.time())

    # Encrypt the complete data package
    json_string = json.dumps(response_data)
    encrypted_data = encrypt(client['shared_secret'], json_string)
    url_safe = quote_plus(encrypted_data)

    return redirect("%s?data=%s" % (redirect_url, url_safe))

def encrypt(key, plaintext):
    padded_text = pkcs7.encode(plaintext, len(key))
    cipher = AES.new(key, AES.MODE_ECB)
    msg = cipher.encrypt(padded_text)
    encoded = base64.b64encode(msg)
    return encoded

def decrypt(key, encoded):
    cipher = AES.new(key, AES.MODE_ECB)
    ciphertext = base64.b64decode(encoded)
    msg_padded = cipher.decrypt(ciphertext)
    msg = pkcs7.decode(msg_padded, len(key))
    return msg
