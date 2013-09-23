# encoding: utf-8
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect

from connect.util import get_request_data, prepare_response
from api.util import get_member_data

def connect(request, method):
    client, request_data, redirect_url = get_request_data(request)

    response_data = {}

    if method == 'bounce':
        response_data['er_autentisert'] = request.user.is_authenticated()

    if request.user.is_authenticated():
        response_data.update(get_member_data(request.user))
    else:
        if method == 'signon':
            request.session['dntconnect'] = {
                'client': client,
                'redirect_url': redirect_url
            }
            return redirect('connect.views.signon_login')
        # The only other method is bounce; in which case we'll just send the response as is

    return prepare_response(client, response_data, redirect_url)

def signon_login(request):
    if not 'dntconnect' in request.session:
        # Use a friendlier error message here?
        raise PermissionDenied

    context = {'client_name': request.session['dntconnect']['client']['friendly_name']}
    return render(request, 'main/connect/signon.html', context)
