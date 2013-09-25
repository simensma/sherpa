# encoding: utf-8
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse

from connect.util import get_request_data, prepare_response
from api.util import get_member_data

import logging

logger = logging.getLogger('sherpa')

def bounce(request):
    client, request_data, redirect_url = get_request_data(request)

    response_data = {'er_autentisert': request.user.is_authenticated()}
    if request.user.is_authenticated():
        response_data.update(get_member_data(request.user))

    return prepare_response(client, response_data, redirect_url)

def signon(request):
    client, request_data, redirect_url = get_request_data(request)

    if not request.user.is_authenticated():
        request.session['dntconnect'] = {
            'client': client,
            'redirect_url': redirect_url
        }
        request.session['innmelding.aktivitet'] = {
            'aktivitet': True, # TODO: Set to the relevant aktivitet-object
            'redirect_url': reverse('connect.views.signon_login'),
        }
        return redirect('connect.views.signon_login')

    response_data = {
        'er_autentisert': request.user.is_authenticated(),
        'signon': u'pålogget',
    }
    response_data.update(get_member_data(request.user))
    return prepare_response(client, response_data, redirect_url)

def signon_login(request):
    if not 'dntconnect' in request.session:
        # Use a friendlier error message here?
        raise PermissionDenied

    if request.user.is_authenticated():
        # The user is redirected back here after authenticating for continuation

        # The signon field should be set in session by whatever service the user used,
        # but it could be missed so check and log any exceptions
        if not 'signon' in request.session['dntconnect']:
            logger.error(u"Mangler 'signon' field i session etter vellykket signon",
                extra={
                    'request': request,
                    'session': request.session,
                    'dntconnect': request.session['dntconnect']
                }
            )

        client = request.session['dntconnect']['client']
        response_data = {
            'er_autentisert': request.user.is_authenticated(),
            'signon': request.session['dntconnect'].get('signon', u'ukjent')
        }
        response_data.update(get_member_data(request.user))
        redirect_url = request.session['dntconnect']['redirect_url']
        del request.session['dntconnect']
        del request.session['innmelding.aktivitet']
        return prepare_response(
            client,
            response_data,
            redirect_url
        )
    else:
        context = {'client_name': request.session['dntconnect']['client']['friendly_name']}
        return render(request, 'main/connect/signon.html', context)
