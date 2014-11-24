# encoding: utf-8
from urllib import quote_plus
from datetime import datetime, timedelta
from Crypto.Cipher import AES
import base64
import json
import time
import os
import sys
import hmac
import hashlib
import logging

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from core import pkcs7

logger = logging.getLogger('sherpa')

def get_request_data(request):
    if not request.GET.get('client', '') in settings.DNT_CONNECT:
        logger.warning(u"DNT Connect: Mangler 'client' GET parameter",
            extra={'request': request}
        )
        raise PermissionDenied
    else:
        client = settings.DNT_CONNECT[request.GET['client']]

    try:
        request_data, auth_index = try_keys(decrypt, client['auths'], request.GET['data'], request.GET.get('hmac'))
        request_data = json.loads(request_data)
    except ValueError:
        logger.warning(u"DNT Connect: ValueError ved dekryptering",
            exc_info=sys.exc_info(),
            extra={
                'request': request,
                'request_data': request_data,
            }
        )
        raise PermissionDenied

    # Check the transmit datestamp
    request_time = datetime.fromtimestamp(request_data['timestamp'])
    if not client['ignore_timestamp_validation'] and datetime.now() - request_time > timedelta(seconds=settings.DNT_CONNECT_TIMEOUT):
        logger.warning(u"DNT Connect: Timestamp validering feilet",
            extra={
                'request': request,
                'request_time': request_time,
                'current_time': datetime.now(),
            }
        )
        raise PermissionDenied

    # Redirect to provided url, or the default if none provided
    redirect_url = request_data['redirect_url'] if 'redirect_url' in request_data else client['default_redirect_url']

    return client, request.GET['client'], auth_index, request_data, redirect_url

def prepare_response(client, auth_index, response_data, redirect_url):
    # Add the current timestamp
    response_data['timestamp'] = int(time.time())

    # Encrypt the complete data package
    json_string = json.dumps(response_data)
    if auth_index is not None:
        # Use the authentication method which worked when decrypting
        encrypted_data, hmac_ = encrypt(client['auths'][auth_index], json_string)
    else:
        # This special case handles old sessions and can likely be removed after a couple of weeks
        encrypted_data, hmac_ = try_keys(encrypt, client['auths'], json_string)[0]
    url_safe_data = quote_plus(encrypted_data)

    if hmac_ is None:
        return redirect("%s?data=%s" % (redirect_url, url_safe_data))
    else:
        url_safe_hmac = quote_plus(hmac_)
        return redirect("%s?data=%s&hmac=%s" % (redirect_url, url_safe_data, url_safe_hmac))

def try_keys(method, auths, *args, **kwargs):
    """
    Encryption and decryption is run through this method which tries all the specified keys, and if one succeeds, uses
    that, if not, raises the exception of the last attempted key.
    """
    last_exception = None
    for auth_index, auth in enumerate(auths):
        try:
            return method(auth, *args, **kwargs), auth_index
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
        hmac_ = calc_hmac(auth['key'], iv + plaintext)
    else:
        cipher = AES.new(auth['key'], auth['cipher'])
        ciphertext = cipher.encrypt(padded_text)
        hmac_ = None

    encoded = base64.b64encode(ciphertext)
    return encoded, hmac_

def decrypt(auth, encoded, hmac_):
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

        if auth['iv'] and calc_hmac(auth['key'], iv + plaintext) != hmac_:
            logger.warning(u"DNT Connect: Forespurt hmac matchet ikke egenkalkulert hmac",
                extra={
                    'our_hmac': calc_hmac(auth['key'], iv + plaintext),
                    'their_hmac': hmac_,
                    'encoded': encoded,
                    'plaintext': plaintext,
                    'auth': auth,
                }
            )
            raise PermissionDenied

        return plaintext
    except TypeError:
        # Can e.g. be incorrect padding if they forgot to URLEncode the data
        logger.warning(u"DNT Connect: TypeError ved dekryptering",
            exc_info=sys.exc_info(),
            extra={
                'auth': auth,
            }
        )
        raise PermissionDenied

def calc_hmac(key, data):
    return base64.b64encode(hmac.new(key, data, hashlib.sha512).digest())

def add_signon_session_value(request, value):
    request.session['dntconnect']['signon'] = value
    request.session.modified = True

def get_member_data(user):
    if not user.is_member():
        return {
            'sherpa_id': user.id,
            'er_medlem': False,
            'fornavn': user.get_first_name(),
            'etternavn': user.get_last_name(),
            'epost': user.get_email()
        }
    else:
        # The gender definition is in norwegian
        def api_gender_output(gender):
            if gender == 'm':
                return 'M'
            elif gender == 'f':
                return 'K'

        address = user.get_address()
        dob = user.get_birth_date()
        if dob is not None:
            dob = dob.strftime("%Y-%m-%d")

        return {
            'sherpa_id': user.id,
            'er_medlem': True,
            'medlemsnummer': user.memberid,
            'aktivt_medlemskap': user.has_paid(),
            'fornavn': user.get_first_name(),
            'etternavn': user.get_last_name(),
            'født': dob,
            'kjønn': api_gender_output(user.get_gender()),
            'epost': user.get_email(),
            'mobil': user.get_phone_mobile(),
            'adresse': {
                'adresse1': address.field1,
                'adresse2': address.field2,
                'adresse3': address.field3,
                'postnummer': address.zipcode.zipcode if address.country.code == 'NO' else None,
                'poststed': address.zipcode.area.title() if address.country.code == 'NO' else None,
                'land': {
                    'kode': address.country.code,
                    'navn': address.country.name
                }
            },
        }
