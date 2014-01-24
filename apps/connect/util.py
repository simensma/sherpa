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
import os

def get_request_data(request):
    if not request.GET.get('client', '') in settings.DNT_CONNECT:
        raise PermissionDenied
    else:
        client = settings.DNT_CONNECT[request.GET['client']]

    request_data = json.loads(try_keys(client['auths'], request.GET['data'], decrypt))

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
    encrypted_data = try_keys(client['auths'], json_string, encrypt)
    url_safe = quote_plus(encrypted_data)

    return redirect("%s?data=%s" % (redirect_url, url_safe))

def try_keys(auths, data, method):
    """
    Encryption and decryption is run through this method which tries all the specified keys, and if one succeeds, uses
    that, if not, raises the exception of the last attempted key.
    """
    last_exception = None
    for auth in auths:
        try:
            return method(auth, data)
        except Exception as e:
            last_exception = e
    # None of the keys worked, raise the last exception
    raise last_exception

def encrypt(auth, plaintext):
    padded_text = pkcs7.encode(plaintext, settings.DNT_CONNECT_BLOCK_SIZE)

    if auth['iv']:
        iv = os.urandom(settings.DNT_CONNECT_BLOCK_SIZE)
        cipher = AES.new(auth['key'], auth['cipher'], iv)
        ciphertext = iv + cipher.encrypt(padded_text)
    else:
        cipher = AES.new(auth['key'], auth['cipher'])
        ciphertext = cipher.encrypt(padded_text)

    encoded = base64.b64encode(ciphertext)
    return encoded

def decrypt(auth, encoded):
    try:
        decoded = base64.b64decode(encoded)

        if auth['iv']:
            iv, ciphertext = decoded[:settings.DNT_CONNECT_BLOCK_SIZE], decoded[settings.DNT_CONNECT_BLOCK_SIZE:]
            cipher = AES.new(auth['key'], auth['cipher'], iv)
        else:
            ciphertext = decoded
            cipher = AES.new(auth['key'], auth['cipher'])

        msg_padded = cipher.decrypt(ciphertext)
        msg = pkcs7.decode(msg_padded, settings.DNT_CONNECT_BLOCK_SIZE)
        return msg
    except TypeError:
        # Can e.g. be incorrect padding if they forgot to URLEncode the data
        raise PermissionDenied

def add_signon_session_value(request, value):
    request.session['dntconnect']['signon'] = value
    request.session.modified = True
