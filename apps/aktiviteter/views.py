import json

from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied
from django.contrib import messages

from sherpa.decorators import user_requires_login
from aktiviteter.models import Aktivitet, AktivitetDate, AktivitetAudience, SimpleParticipant, Cabin
from aktiviteter.util import filter_aktivitet_dates, paginate_aktivitet_dates
from core import validator
from foreninger.models import Forening
from turbasen.models import Omrade

def index(request):
    filter, aktivitet_dates = filter_aktivitet_dates(request.GET)
    aktivitet_dates_pagenav = paginate_aktivitet_dates(filter, aktivitet_dates)

    context = {
        'aktivitet_dates': aktivitet_dates_pagenav,
        'difficulties': Aktivitet.DIFFICULTY_CHOICES,
        'categories': Aktivitet.CATEGORY_CHOICES,
        'category_types': Aktivitet.CATEGORY_TYPES_LIST,
        'audiences': AktivitetAudience.AUDIENCE_CHOICES,
        'omrader': sorted(Omrade.lookup(), key=lambda o: o.navn),
        'all_foreninger': Forening.get_all_sorted_with_type_data(),
        'cabins': Cabin.objects.order_by('name'),
        'filter': filter,
    }
    return render(request, 'common/aktiviteter/index.html', context)

def filter(request):
    if not request.is_ajax() or not request.method == 'POST':
        return redirect('aktiviteter.views.index')

    filter, aktivitet_dates = filter_aktivitet_dates(request.POST)
    aktivitet_dates_pagenav = paginate_aktivitet_dates(filter, aktivitet_dates)

    context = RequestContext(request, {
        'aktivitet_dates': aktivitet_dates_pagenav
    })
    return HttpResponse(json.dumps({
        'html': render_to_string('common/aktiviteter/listing.html', context),
        'page': aktivitet_dates_pagenav.number,
    }))

def show(request, aktivitet_date):
    try:
        aktivitet_date = AktivitetDate.get_published().get(id=aktivitet_date)
    except AktivitetDate.DoesNotExist:
        raise Http404

    context = {
        'hide_unpublished_warning': True,
        'aktivitet_date': aktivitet_date,
        'user_is_participating': request.user.is_authenticated() and request.user in aktivitet_date.participants.all()
    }
    return render(request, 'common/aktiviteter/show/show.html', context)

def signup(request, aktivitet_date):
    try:
        aktivitet_date = AktivitetDate.get_published().get(id=aktivitet_date)
    except AktivitetDate.DoesNotExist:
        raise Http404

    if not aktivitet_date.accepts_signups():
        raise PermissionDenied
    if request.user.is_authenticated():
        return redirect('aktiviteter.views.signup_logged_on', aktivitet_date.id)
    else:
        return redirect('aktiviteter.views.signup_not_logged_on', aktivitet_date.id)

def signup_not_logged_on(request, aktivitet_date):
    try:
        aktivitet_date = AktivitetDate.get_published().get(id=aktivitet_date)
    except AktivitetDate.DoesNotExist:
        raise Http404

    if request.user.is_authenticated():
        return redirect('aktiviteter.views.signup_logged_on', aktivitet_date.id)
    if not aktivitet_date.accepts_signups():
        raise PermissionDenied
    context = {'aktivitet_date': aktivitet_date}
    return render(request, 'common/aktiviteter/signup_not_logged_on.html', context)

def signup_simple(request, aktivitet_date):
    try:
        aktivitet_date = AktivitetDate.get_published().get(id=aktivitet_date)
    except AktivitetDate.DoesNotExist:
        raise Http404

    if not aktivitet_date.accepts_signups() or not aktivitet_date.signup_simple_allowed:
        raise PermissionDenied

    errors = False

    name = request.POST['name'].strip()
    phone = request.POST['phone'].strip()
    email = request.POST['email'].strip()

    if not validator.name(name):
        messages.error(request, 'simple_signup_name_invalid')
        errors = True

    if not validator.phone(phone, req=False):
        messages.error(request, 'simple_signup_phone_invalid')
        errors = True

    if not validator.email(email, req=False):
        messages.error(request, 'simple_signup_email_invalid')
        errors = True

    if phone == '' and email == '':
        messages.error(request, 'simple_signup_phone_or_email_required')
        errors = True

    if errors:
        return redirect('aktiviteter.views.signup_not_logged_on', aktivitet_date.id)

    participant = SimpleParticipant(
        aktivitet_date=aktivitet_date,
        name=request.POST['name'],
        email=request.POST['name'],
        phone=request.POST['name']
    )
    participant.save()
    return redirect('aktiviteter.views.signup_not_logged_on', aktivitet_date.id)

@user_requires_login()
def signup_logged_on(request, aktivitet_date):
    try:
        aktivitet_date = AktivitetDate.get_published().get(id=aktivitet_date)
    except AktivitetDate.DoesNotExist:
        raise Http404

    if not aktivitet_date.accepts_signups():
        raise PermissionDenied
    context = {'aktivitet_date': aktivitet_date}
    return render(request, 'common/aktiviteter/signup_logged_on.html', context)

@user_requires_login()
def signup_confirm(request, aktivitet_date):
    try:
        aktivitet_date = AktivitetDate.get_published().get(id=aktivitet_date)
    except AktivitetDate.DoesNotExist:
        raise Http404

    if not aktivitet_date.accepts_signups():
        raise PermissionDenied
    aktivitet_date.participants.add(request.user)
    return redirect('aktiviteter.views.show', aktivitet_date.id)

@user_requires_login()
def signup_cancel(request, aktivitet_date):
    try:
        aktivitet_date = AktivitetDate.get_published().get(id=aktivitet_date)
    except AktivitetDate.DoesNotExist:
        raise Http404

    if not aktivitet_date.accepts_signup_cancels():
        raise PermissionDenied
    context = {'aktivitet_date': aktivitet_date}
    return render(request, 'common/aktiviteter/signup_cancel.html', context)

@user_requires_login()
def signup_cancel_confirm(request, aktivitet_date):
    try:
        aktivitet_date = AktivitetDate.get_published().get(id=aktivitet_date)
    except AktivitetDate.DoesNotExist:
        raise Http404

    if not aktivitet_date.accepts_signup_cancels():
        raise PermissionDenied
    aktivitet_date.participants.remove(request.user)
    messages.info(request, 'signup_cancel_success')
    return redirect('user.views.aktiviteter')
