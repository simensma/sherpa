# encoding: utf-8
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.core.exceptions import PermissionDenied
from Crypto.Cipher import AES

from urllib import quote_plus
import json
import base64

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
        if request.user.get_profile().is_member():
            data = json.dumps({
                'sherpa_id': request.user.get_profile().id,
                'fornavn': request.user.get_profile().get_first_name(),
                'etternavn': request.user.get_profile().get_last_name(),
                'epost': request.user.get_profile().get_email()
            })
        else:
            data = json.dumps({
                'sherpa_id': request.user.get_profile().id,
                'memberid': request.user.get_profile().memberid
                # Todo: Legg inn alle parameterne
            })

    encrypted_data = encrypt(client['shared_secret'], data)

    url_safe = quote_plus(encrypted_data)

    redirect_url = request.GET['redirect_url'] if request.GET.get('redirect_url') is not None else client['default_redirect_url']
    return HttpResponseRedirect("%s?data=%s" % (redirect_url, url_safe))

def receive(request):
    key = settings.DNT_CONNECT['ut']['shared_secret']
    decrypted = decrypt(key, request.GET['data'])
    return HttpResponse(decrypted)

def encrypt(key, plaintext):
    padded_text = plaintext + (settings.DNT_CONNECT_BLOCK_SIZE - len(plaintext) % settings.DNT_CONNECT_BLOCK_SIZE) * '\0'
    cipher = AES.new(key, AES.MODE_ECB)
    msg = cipher.encrypt(padded_text)
    encoded = base64.b64encode(msg)
    return encoded

def decrypt(key, encoded):
    cipher = AES.new(key, AES.MODE_ECB)
    ciphertext = base64.b64decode(encoded)
    msg = cipher.decrypt(ciphertext).rstrip('\x00')
    return msg
