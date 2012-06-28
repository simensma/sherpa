from django.core.urlresolvers import reverse
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login as log_user_in, logout as log_user_out
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template import Context, loader
from django.utils import crypto
from django.db.utils import IntegrityError

from datetime import datetime, timedelta
import json
import md5
import re

from analytics.models import Visitor, Request
from user.models import Profile

update_success = 'oppdatert'
PHONE_MAX_LENGTH = 20 # Magic number copied from user.models.Profile.phone.max_length

def home(request):
    return HttpResponseRedirect('https://%s/minside/' % settings.OLD_SITE)

@login_required
def home_new(request):
    return render(request, 'user/home.html')

@login_required
def account(request):
    context = {'password_length': settings.USER_PASSWORD_LENGTH,
        'update_success': request.GET.has_key(update_success),
        'phone_max_length': PHONE_MAX_LENGTH}
    if request.method == 'POST':
        try:
            if len(request.POST['name']) == 0:
                raise ValueError("No name provided")
            if len(re.findall('.+@.+\..+', request.POST['email'])) == 0:
                raise ValueError("Invalid email address")
            if len(request.POST['password']) > 0 and len(request.POST['password']) < settings.USER_PASSWORD_LENGTH:
                raise ValueError("Password too short (minimum %s)" % settings.USER_PASSWORD_LENGTH)
            if len(request.POST['phone']) > PHONE_MAX_LENGTH:
                context['phone_too_long'] = True
                return render(request, 'user/account.html', context)
            split = request.POST['name'].split(' ')
            first_name = split[0]
            last_name = ' '.join(split[1:])
            request.user.username = username(request.POST['email'])
            request.user.email = request.POST['email']
            if len(request.POST['password']) > 0:
                request.user.set_password(request.POST['password'])
            request.user.first_name = first_name
            request.user.last_name = last_name
            request.user.save()
            profile = request.user.get_profile()
            profile.phone = request.POST['phone']
            profile.save()
            return HttpResponseRedirect("%s?%s" % (reverse('user.views.account'), update_success))
        except ValueError:
            context['value_error'] = True
        except IntegrityError as e:
            context['integrity_error'] = True
    return render(request, 'user/account.html', context)

def login(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            # User is already authenticated, skip login
            return HttpResponseRedirect(request.GET.get('next', reverse('user.views.home_new')))
        context = {'next': request.GET.get('next')}
        return render(request, 'user/login.html', context)
    elif request.method == 'POST':
        user = authenticate(username=username(request.POST['email']), password=request.POST['password'])
        if user is not None:
            merge_visitor(request.session, user.get_profile())
            log_user_in(request, user)
            return HttpResponseRedirect(request.GET.get('next', reverse('user.views.home_new')))
        else:
            context = {'invalid_credentials': True, 'next': request.GET.get('next')}
            return render(request, 'user/login.html', context)

def logout(request):
    log_user_out(request)
    return HttpResponseRedirect(reverse('page.views.page'))

def merge_visitor(session, profile):
    visitor = Visitor.objects.get(id=session['visitor'])
    if visitor.profile == profile:
        # The user already has connected this visitor to the correct profile
        # This might happen if the user logs in twice, somehow.
        return
    if visitor.profile != None:
        # Whoa! The user has connected this visitor to a _different_ profile!
        # Could this ever happen? We should probably log this and analyze
        # what happened, if it occurs.
        return
    if Visitor.objects.filter(profile=profile).exists():
        # The user's profile already has a Visitor, so merge all the
        # requests over and delete the 'extra' visitor
        requests = Request.objects.filter(visitor=visitor)
        for request in requests:
            request.visitor = profile.visitor
            request.save()
        visitor.delete()
        session['visitor'] = profile.visitor.id
    else:
        # The user's profile didn't have an existing Visitor, so just
        # apply this one to the profile
        visitor.profile = profile
        visitor.save()

def send_restore_password_email(request):
    try:
        user = User.objects.get(email=request.POST['email'])
    except User.DoesNotExist:
        return HttpResponse(json.dumps({'status': 'invalid_email'}))
    profile = user.get_profile()
    key = crypto.get_random_string(length=settings.RESTORE_PASSWORD_KEY_LENGTH)
    profile.password_restore_key = key
    profile.password_restore_date = datetime.now()
    profile.save()
    t = loader.get_template('user/restore-password-email.html')
    c = Context({'user': user})
    user.email_user("Gjenopprettelse av passord", t.render(c))
    return HttpResponse(json.dumps({'status': 'success'}))

def restore_password(request, key):
    try:
        profile = Profile.objects.get(password_restore_key=key)
    except Profile.DoesNotExist:
        context = {'no_such_key': True}
        return render(request, 'user/restore-password.html', context)
    deadline = profile.password_restore_date + timedelta(hours=settings.RESTORE_PASSWORD_VALIDITY)
    if datetime.now() > deadline:
        # We've passed the deadline for key validity
        context = {'key_expired': True, 'validity_period': settings.RESTORE_PASSWORD_VALIDITY}
        return render(request, 'user/restore-password.html', context)

    # Passed all tests, looks like we're ready to reset the password
    if request.method == 'GET':
        context = {'ready': True, 'key': key, 'password_length': settings.USER_PASSWORD_LENGTH}
        return render(request, 'user/restore-password.html', context)
    elif request.method == 'POST':
        if request.POST['password'] != request.POST['password-duplicate'] or len(request.POST['password']) < settings.USER_PASSWORD_LENGTH:
            context = {'ready': True, 'key': key, 'password_length': settings.USER_PASSWORD_LENGTH,
                'unacceptable_password': True}
            return render(request, 'user/restore-password.html', context)
        # Everything is in order. Reset the password.
        profile.user.set_password(request.POST['password'])
        profile.user.save()
        profile.password_restore_key = None
        profile.password_restore_date = None
        profile.save()
        context = {'success': True}
        return render(request, 'user/restore-password.html', context)

# This returns a username value based on the email address.
# Define it as the first 30 hex-characters of the MD5 hash of the stripped, lowercase email.
# This is because the username field has a 30 character max length, which makes it unsuitable for
# actual e-mail addresses. This gives a 16^30 collision chance which is acceptable.
def username(email):
    return md5.new(email.strip().lower()).hexdigest()[:30]
