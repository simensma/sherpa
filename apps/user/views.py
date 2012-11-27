from django.core.urlresolvers import reverse
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login as log_user_in, logout as log_user_out
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.template import RequestContext, loader
from django.utils import crypto
from django.db.utils import IntegrityError

from datetime import datetime, timedelta
import json
import md5
import re

from user.models import Profile
from core import validator

def home(request):
    return HttpResponseRedirect('https://%s/minside/' % settings.OLD_SITE)

@login_required
def home_new(request):
    return render(request, 'common/user/home.html')

@login_required
def account(request):
    context = {
        'password_length': settings.USER_PASSWORD_LENGTH,
        'phone_max_length': Profile.PHONE_MAX_LENGTH}
    return render(request, 'common/user/account.html', context)

@login_required
def update_account(request):
    errors = False

    if not validator.name(request.POST['name']):
        messages.error(request, 'no_name_provided')
        errors = True

    if not validator.email(request.POST['email']):
        messages.error(request, 'invalid_email_address')
        errors = True

    if User.objects.filter(email=request.POST['email']).exclude(id=request.user.id).exists():
        messages.error(request, 'duplicate_email_address')
        errors = True

    if len(request.POST['phone']) > Profile.PHONE_MAX_LENGTH:
        messages.error(request, 'phone_too_long')
        errors = True

    if not errors:
        split = request.POST['name'].split(' ')
        first_name = split[0]
        last_name = ' '.join(split[1:])
        request.user.username = username(request.POST['email'])
        request.user.email = request.POST['email']
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.save()
        profile = request.user.get_profile()
        profile.phone = request.POST['phone']
        profile.save()
        messages.info(request, 'update_success')

    return HttpResponseRedirect(reverse('user.views.account'))

@login_required
def update_account_password(request):
    if len(request.POST['password']) < settings.USER_PASSWORD_LENGTH:
        messages.error(request, 'password_too_short')
    else:
        request.user.set_password(request.POST['password'])
        request.user.save()
        messages.info(request, 'password_update_success')
    return HttpResponseRedirect(reverse('user.views.account'))

def login(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            # User is already authenticated, skip login
            return HttpResponseRedirect(request.GET.get('next', reverse('user.views.home_new')))
        context = {'next': request.GET.get('next')}
        return render(request, 'common/user/login.html', context)
    elif request.method == 'POST':
        user = authenticate(username=username(request.POST['email']), password=request.POST['password'])
        if user is not None:
            log_user_in(request, user)
            return HttpResponseRedirect(request.GET.get('next', reverse('user.views.home_new')))
        else:
            context = {'invalid_credentials': True, 'next': request.GET.get('next')}
            return render(request, 'common/user/login.html', context)

def logout(request):
    log_user_out(request)
    return HttpResponseRedirect(reverse('page.views.page'))

def register(request):
    return render(request, 'common/user/register.html')

def send_restore_password_email(request):
    try:
        user = User.objects.get(email=request.POST['email'])
    except (User.DoesNotExist, KeyError):
        return HttpResponse(json.dumps({'status': 'invalid_email'}))
    profile = user.get_profile()
    key = crypto.get_random_string(length=settings.RESTORE_PASSWORD_KEY_LENGTH)
    profile.password_restore_key = key
    profile.password_restore_date = datetime.now()
    profile.save()
    t = loader.get_template('common/user/restore-password-email.html')
    c = RequestContext(request, {
        'found_user': user,
        'validity_period': settings.RESTORE_PASSWORD_VALIDITY})
    user.email_user("Gjenopprettelse av passord", t.render(c))
    return HttpResponse(json.dumps({'status': 'success'}))

def restore_password(request, key):
    try:
        profile = Profile.objects.get(password_restore_key=key)
    except Profile.DoesNotExist:
        context = {'no_such_key': True}
        return render(request, 'common/user/restore-password.html', context)
    deadline = profile.password_restore_date + timedelta(hours=settings.RESTORE_PASSWORD_VALIDITY)
    if datetime.now() > deadline:
        # We've passed the deadline for key validity
        context = {'key_expired': True, 'validity_period': settings.RESTORE_PASSWORD_VALIDITY}
        return render(request, 'common/user/restore-password.html', context)

    # Passed all tests, looks like we're ready to reset the password
    if request.method == 'GET':
        context = {'ready': True, 'key': key, 'password_length': settings.USER_PASSWORD_LENGTH}
        return render(request, 'common/user/restore-password.html', context)
    elif request.method == 'POST':
        if request.POST['password'] != request.POST['password-duplicate'] or len(request.POST['password']) < settings.USER_PASSWORD_LENGTH:
            context = {'ready': True, 'key': key, 'password_length': settings.USER_PASSWORD_LENGTH,
                'unacceptable_password': True}
            return render(request, 'common/user/restore-password.html', context)
        # Everything is in order. Reset the password.
        profile.user.set_password(request.POST['password'])
        profile.user.save()
        profile.password_restore_key = None
        profile.password_restore_date = None
        profile.save()
        context = {'success': True}
        return render(request, 'common/user/restore-password.html', context)

# This returns a username value based on the email address.
# Define it as the first 30 hex-characters of the MD5 hash of the stripped, lowercase email.
# This is because the username field has a 30 character max length, which makes it unsuitable for
# actual e-mail addresses. This gives a 16^30 collision chance which is acceptable.
def username(email):
    return md5.new(email.strip().lower()).hexdigest()[:30]
