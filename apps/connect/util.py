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
import hashlib
import logging

logger = logging.getLogger('sherpa')

def get_request_data(request):
    if not request.GET.get('client', '') in settings.DNT_CONNECT:
        raise PermissionDenied
    else:
        client = settings.DNT_CONNECT[request.GET['client']]

    request_data = json.loads(try_keys(decrypt, client['auths'], request.GET['data'], request.GET.get('hash')))

    # Check the transmit datestamp
    request_time = datetime.fromtimestamp(request_data['timestamp'])
    if datetime.now() - request_time > timedelta(seconds=settings.DNT_CONNECT_TIMEOUT):
        raise PermissionDenied

    # Redirect to provided url, or the default if none provided
    redirect_url = request_data['redirect_url'] if 'redirect_url' in request_data else client['default_redirect_url']

    return client, request.GET['client'], request_data, redirect_url

def prepare_response(client, response_data, redirect_url):
    # Add the current timestamp
    response_data['timestamp'] = int(time.time())

    # Encrypt the complete data package
    json_string = json.dumps(response_data)
    encrypted_data, hash = try_keys(encrypt, client['auths'], json_string)
    url_safe_data = quote_plus(encrypted_data)

    if hash is None:
        return redirect("%s?data=%s" % (redirect_url, url_safe_data))
    else:
        url_safe_hash = quote_plus(hash)
        return redirect("%s?data=%s&hash=%s" % (redirect_url, url_safe_data, url_safe_hash))

def try_keys(method, auths, *args, **kwargs):
    """
    Encryption and decryption is run through this method which tries all the specified keys, and if one succeeds, uses
    that, if not, raises the exception of the last attempted key.
    """
    last_exception = None
    for auth in auths:
        try:
            return method(auth, *args, **kwargs)
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
        hash = calc_hash(auth['key'], iv + plaintext)
    else:
        cipher = AES.new(auth['key'], auth['cipher'])
        ciphertext = cipher.encrypt(padded_text)
        hash = None

    encoded = base64.b64encode(ciphertext)
    return encoded, hash

def decrypt(auth, encoded, hash):
    try:
        decoded = base64.b64decode(encoded)

        if auth['iv']:
            iv, ciphertext = decoded[:settings.DNT_CONNECT_BLOCK_SIZE], decoded[settings.DNT_CONNECT_BLOCK_SIZE:]
            cipher = AES.new(auth['key'], auth['cipher'], iv)
        else:
            ciphertext = decoded
            cipher = AES.new(auth['key'], auth['cipher'])

        plaintext_padded = cipher.decrypt(ciphertext)
        plaintext = pkcs7.decode(plaintext_padded, settings.DNT_CONNECT_BLOCK_SIZE)

        if auth['iv'] and calc_hash(auth['key'], iv + plaintext) != hash:
            logger.warning(u"Forespurt hash matchet ikke egenkalkulert hash",
                extra={
                    'our_hash': calc_hash(auth['key'], iv + plaintext),
                    'their_hash': hash,
                    'encoded': encoded,
                    'plaintext': plaintext,
                    'auth': auth,
                }
            )
            raise PermissionDenied

        return plaintext
    except TypeError:
        # Can e.g. be incorrect padding if they forgot to URLEncode the data
        raise PermissionDenied

def calc_hash(key, data):
    h = hashlib.sha512(key)
    h.update(data)
    return base64.b64encode(h.hexdigest())

def add_signon_session_value(request, value):
    request.session['dntconnect']['signon'] = value
    request.session.modified = True
