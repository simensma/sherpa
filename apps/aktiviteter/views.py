from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied
from django.contrib import messages

import json

from sherpa.decorators import user_requires_login
from aktiviteter.models import Aktivitet, AktivitetDate

def index(request):
    aktivitet_dates = AktivitetDate.get_published().exclude(
        aktivitet__hidden=True
    ).order_by(
        '-start_date'
    )
    aktivitet_positions = Aktivitet.get_published().filter(start_point__isnull=False)
    aktivitet_positions_json = json.dumps([{
        'id': a.id,
        'lat': a.start_point.get_coords()[0],
        'lng': a.start_point.get_coords()[1]
    } for a in aktivitet_positions])
    context = {
        'aktivitet_dates': aktivitet_dates,
        'aktivitet_positions': aktivitet_positions,
        'aktivitet_positions_json': aktivitet_positions_json,
        'difficulties': Aktivitet.DIFFICULTY_CHOICES
    }
    return render(request, 'common/aktiviteter/index.html', context)

def show(request, aktivitet_date):
    aktivitet_date = AktivitetDate.get_published().get(id=aktivitet_date)
    context = {
        'aktivitet_date': aktivitet_date,
        'user_is_participating': request.user.get_profile() in aktivitet_date.participants.all()
    }
    return render(request, 'common/aktiviteter/show.html', context)

@user_requires_login()
def signup(request, aktivitet_date):
    aktivitet_date = AktivitetDate.get_published().get(id=aktivitet_date)
    if not aktivitet_date.accepts_signups():
        raise PermissionDenied
    context = {'aktivitet_date': aktivitet_date}
    return render(request, 'common/aktiviteter/signup.html', context)

@user_requires_login()
def signup_confirm(request, aktivitet_date):
    aktivitet_date = AktivitetDate.get_published().get(id=aktivitet_date)
    if not aktivitet_date.accepts_signups():
        raise PermissionDenied
    aktivitet_date.participants.add(request.user.get_profile())
    return redirect('aktiviteter.views.show', aktivitet_date.id)

@user_requires_login()
def signup_cancel(request, aktivitet_date):
    aktivitet_date = AktivitetDate.get_published().get(id=aktivitet_date)
    if not aktivitet_date.accepts_signup_cancels():
        raise PermissionDenied
    context = {'aktivitet_date': aktivitet_date}
    return render(request, 'common/aktiviteter/signup_cancel.html', context)

@user_requires_login()
def signup_cancel_confirm(request, aktivitet_date):
    aktivitet_date = AktivitetDate.get_published().get(id=aktivitet_date)
    if not aktivitet_date.accepts_signup_cancels():
        raise PermissionDenied
    aktivitet_date.participants.remove(request.user.get_profile())
    messages.info(request, 'signup_cancel_success')
    return redirect('user.views.aktiviteter')
