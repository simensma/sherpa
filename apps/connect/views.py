# encoding: utf-8
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.core.exceptions import PermissionDenied
from Crypto.Cipher import AES

from urllib import quote_plus
import json
import base64

from core import pkcs7

def connect(request):

    if not request.GET.get('client', '') in settings.DNT_CONNECT:
        raise PermissionDenied
    else:
        client = settings.DNT_CONNECT[request.GET['client']]

    data = None

    if request.user.is_anonymous():
        data = json.dumps({
            'status': 'not logged on'
        })
    else:
        memberdata = get_member_data(request.user)
        return memberdata

    encrypted_data = encrypt(client['shared_secret'], data)

    url_safe = quote_plus(encrypted_data)

    redirect_url = request.GET['redirect_url'] if request.GET.get('redirect_url') is not None else client['default_redirect_url']
    return HttpResponseRedirect("%s?data=%s" % (redirect_url, url_safe))

def receive(request):
    key = settings.DNT_CONNECT['ut']['shared_secret']
    decrypted = decrypt(key, request.GET['data'])
    return HttpResponse(decrypted)

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
