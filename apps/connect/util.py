from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from Crypto.Cipher import AES
from core import pkcs7

from urllib import quote_plus
from datetime import datetime, timedelta
import base64
import json
import time

def get_request_data(request):
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
    redirect_url = request_data['redirect_url'] if 'redirect_url' in request_data else client['default_redirect_url']

    return client, request_data, redirect_url

def prepare_response(client, response_data, redirect_url):
    # Add the current timestamp
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
