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

    response_data = {}

    if method == 'bounce':
        response_data['er_autentisert'] = request.user.is_authenticated()

    if request.user.is_authenticated():
        response_data.update(get_member_data(request.user))
    else:
        if method == 'signon':
            # TODO: Redirect to login/registration page
            pass
        # The only other method is bounce; in which case we'll just send the response as is

    # Append the current timestamp
    response_data['timestamp'] = int(time.time())

    # Encrypt the complete data package
    json_string = json.dumps(response_data)
    encrypted_data = encrypt(client['shared_secret'], json_string)
    url_safe = quote_plus(encrypted_data)

    # Redirect to provided url, or the default if none provided
    redirect_url = request.GET['redirect_url'] if request.GET.get('redirect_url') is not None else client['default_redirect_url']
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

def get_member_data(user):
    if not user.get_profile().is_member():
        return {
            'sherpa_id': user.get_profile().id,
            'er_medlem': False,
            'fornavn': user.get_profile().get_first_name(),
            'etternavn': user.get_profile().get_last_name(),
            'epost': user.get_profile().get_email()
        }
    else:
        # The gender definition is in norwegian
        def api_gender_output(gender):
            if gender == 'm':
                return 'M'
            elif gender == 'f':
                return 'K'

        address = user.get_profile().get_actor().get_clean_address()
        return {
            'sherpa_id': user.get_profile().id,
            'er_medlem': True,
            'medlemsnummer': user.get_profile().memberid,
            'aktivt_medlemskap': user.get_profile().get_actor().has_paid(),
            'etternavn': user.get_profile().get_last_name(),
            'fornavn': user.get_profile().get_first_name(),
            'etternavn': user.get_profile().get_last_name(),
            'født': user.get_profile().get_actor().birth_date.strftime("%Y-%m-%d"),
            'kjønn': api_gender_output(user.get_profile().get_actor().get_gender()),
            'epost': user.get_profile().get_email(),
            'mobil': user.get_profile().get_actor().phone_mobile,
            'address': {
                'adresse1': address.field1,
                'adresse2': address.field2,
                'adresse3': address.field3,
                'postnummer': address.zipcode.zipcode if address.country.code == 'NO' else None,
                'poststed': address.zipcode.area.title() if address.country.code == 'NO' else None,
                'land': {
                    'kode': address.country.code,
                    'navn': address.country.name
                }
            }
        }
