from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login as log_user_in, logout as log_user_out
from django.contrib.auth.models import User
from django.contrib import messages
from django.template import RequestContext, loader
from django.utils import crypto

from datetime import datetime, timedelta
import json, re

from user.models import Profile
from focus.models import Actor
from user.util import username

from core import validator

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
    if request.method == 'GET':
        # TODO: Should refill form with values upon error and redirect back here
        context = {
            'user_password_length': settings.USER_PASSWORD_LENGTH
        }
        return render(request, 'common/user/registration.html', context)
    elif request.method == 'POST':
        try:
            # Check that the password is long enough
            if len(request.POST['password']) < settings.USER_PASSWORD_LENGTH:
                messages.error(request, 'too_short_password')
                return HttpResponseRedirect(reverse('user.login.views.register'))

            # Check that the email address is valid
            if not validator.email(request.POST['email']):
                messages.error(request, 'invalid_email')
                return HttpResponseRedirect(reverse('user.login.views.register'))

            # Check that the memberid is correct (and retrieve the Actor-entry)
            actor = Actor.objects.get(memberid=request.POST['memberid'], address__zipcode=request.POST['zipcode'])

            # Check that the user doesn't already have an account
            if Profile.objects.filter(memberid=request.POST['memberid']).exists():
                messages.error(request, 'profile_exists')
                return HttpResponseRedirect(reverse('user.login.views.register'))

            # Check that the email address isn't in use
            if User.objects.filter(username=username(request.POST['email'])).exists():
                # Note! This COULD be a collision based on our username-algorithm (and pigs COULD fly)
                messages.error(request, 'email_exists')
                return HttpResponseRedirect(reverse('user.login.views.register'))

            user = User.objects.create_user(username(actor.email), password=request.POST['password'])
            profile = Profile(user=user, memberid=actor.memberid)
            profile.save()
            log_user_in(request, authenticate(username=user.username, password=request.POST['password']))
            return HttpResponseRedirect(reverse('user.views.home_new'))
        except (Actor.DoesNotExist, ValueError):
            messages.error(request, 'invalid_memberid')
            return HttpResponseRedirect(reverse('user.login.views.register'))

def verify_memberid(request):
    try:
        actor = Actor.objects.get(memberid=request.POST['memberid'], address__zipcode=request.POST['zipcode'])
        return HttpResponse(json.dumps({
            'exists': True,
            'name': "%s %s" % (actor.first_name, actor.last_name),
            'email': actor.email or '',
            'profile_exists': Profile.objects.filter(memberid=request.POST['memberid']).exists()}))
    except (ValueError, Actor.DoesNotExist):
        return HttpResponse(json.dumps({'exists': False}))

def send_restore_password_email(request):
    try:
        profile = User.objects.get(email=request.POST['email']).get_profile()
    except User.DoesNotExist:
        try:
            actor = Actor.objects.get(email=request.POST['email'])
            profile = Profile.objects.get(memberid=actor.memberid)
        except Actor.DoesNotExist:
            return HttpResponse(json.dumps({'status': 'invalid_email'}))
    except KeyError:
        return HttpResponse(json.dumps({'status': 'invalid_email'}))
    key = crypto.get_random_string(length=settings.RESTORE_PASSWORD_KEY_LENGTH)
    profile.password_restore_key = key
    profile.password_restore_date = datetime.now()
    profile.save()
    t = loader.get_template('common/user/restore-password-email.html')
    c = RequestContext(request, {
        'found_user': profile.user,
        'validity_period': settings.RESTORE_PASSWORD_VALIDITY})
    send_mail("Gjenopprettelse av passord", t.render(c), settings.DEFAULT_FROM_EMAIL, [profile.get_email()])
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
