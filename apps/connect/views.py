# encoding: utf-8
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login as log_user_in

from connect.util import get_request_data, prepare_response, add_signon_session_value
from api.util import get_member_data
from user.login.util import attempt_login
from user.models import User

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

    request.session['dntconnect'] = {
        'client': client,
        'redirect_url': redirect_url
    }
    if not request.user.is_authenticated():
        request.session['innmelding.aktivitet'] = {
            'aktivitet': True, # TODO: Set to the relevant aktivitet-object
            'redirect_url': reverse('connect.views.signon_login'),
        }
        return redirect('connect.views.signon_login')
    else:
        # A bit slower, but cleaner, to redirect an extra time even though we could
        # just redirect back to the client directly from here.
        request.session['dntconnect']['signon'] = u'pålogget'
        return redirect('connect.views.signon_complete')

def signon_login(request):
    if not 'dntconnect' in request.session:
        # Use a friendlier error message here?
        raise PermissionDenied

    if request.user.is_authenticated():
        # Shouldn't happen, but handle it just in case.
        return redirect('connect.views.signon_complete')
    else:
        if request.method == 'GET':
            context = {
                'client_name': request.session['dntconnect']['client']['friendly_name'],
                'user_password_length': settings.USER_PASSWORD_LENGTH,
            }
            return render(request, 'main/connect/signon.html', context)
        else:
            matches, message = attempt_login(request)

            if len(matches) == 1:
                add_signon_session_value(request, 'logget_inn')
                return redirect('connect.views.signon_complete')

            elif len(matches) > 1:
                # Multiple matches, offer a choice between all matches
                request.session['authenticated_users'] = [u.id for u in matches]
                return redirect('connect.views.signon_choose_authenticated_user')

            else:
                messages.error(request, message)
                context = {
                    'email': request.POST['email']
                }
                return render(request, 'main/connect/signon.html', context)

def signon_choose_authenticated_user(request):
    if not 'authenticated_users' in request.session or not 'dntconnect' in request.session:
        raise PermissionDenied

    users = User.get_users(include_pending=True).filter(id__in=request.session['authenticated_users'], is_active=True)
    context = {
        'users': sorted(users, key=lambda u: u.get_first_name())
    }
    return render(request, 'main/connect/signon_choose_authenticated_user.html', context)

def signon_login_chosen_user(request):
    if not 'authenticated_users' in request.session or not 'dntconnect' in request.session:
        raise PermissionDenied

    if not 'user' in request.POST:
        del request.session['authenticated_users']
        return redirect('connect.views.signon_login')

    # Verify that the user authenticated for this user
    if not int(request.POST['user']) in request.session['authenticated_users']:
        del request.session['authenticated_users']
        return redirect('connect.views.signon_login')

    # All is swell, log the user in
    user = User.get_users(include_pending=True).get(id=request.POST['user'], is_active=True)
    user = authenticate(user=user)
    log_user_in(request, user)
    add_signon_session_value(request, 'logget_inn')
    del request.session['authenticated_users']
    return redirect('connect.views.signon_complete')

def signon_complete(request):
    if not 'dntconnect' in request.session or not request.user.is_authenticated():
        # Use a friendlier error message here?
        raise PermissionDenied

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
    if 'innmelding.aktivitet' in request.session:
        del request.session['innmelding.aktivitet']
    return prepare_response(
        client,
        response_data,
        redirect_url
    )
