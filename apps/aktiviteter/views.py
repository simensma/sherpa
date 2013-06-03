from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.contrib import messages

from sherpa.decorators import user_requires_login
from aktiviteter.models import Aktivitet, AktivitetDate

def index(request):
    aktivitet_dates = AktivitetDate.get_published().exclude(
        aktivitet__hidden=True
    ).order_by(
        '-start_date'
    )
    context = {
        'aktivitet_dates': aktivitet_dates,
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
    return HttpResponseRedirect(reverse('aktiviteter.views.show', args=[aktivitet_date.id]))

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
    return HttpResponseRedirect(reverse('user.views.aktiviteter'))