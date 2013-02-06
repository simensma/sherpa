# encoding: utf-8
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
from user.util import username, memberid_lookups_exceeded, authenticate_sherpa2_user

from core import validator

EMAIL_REGISTERED_SUBJECT = u"Velkommen som bruker på DNTs nettsted"
EMAIL_REGISTERED_NONMEMBER_SUBJECT = EMAIL_REGISTERED_SUBJECT

def login(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            # User is already authenticated, skip login
            return HttpResponseRedirect(request.GET.get('next', reverse('user.views.home_new')))
        context = {'next': request.GET.get('next')}
        return render(request, 'common/user/login/login.html', context)
    elif request.method == 'POST':
        user = authenticate(username=username(request.POST['email']), password=request.POST['password'])
        if user is not None:
            log_user_in(request, user)
            return HttpResponseRedirect(request.GET.get('next', reverse('user.views.home_new')))
        else:
            old_member = authenticate_sherpa2_user(request.POST['email'], request.POST['password'])
            if old_member is not None:
                if Profile.objects.filter(memberid=old_member.memberid).exists():
                    messages.error(request, 'old_memberid_but_memberid_exists')
                    return render(request, 'common/user/login/login.html')

                if User.objects.filter(username=username(request.POST['email'])):
                    messages.error(request, 'old_memberid_but_email_exists')
                    return render(request, 'common/user/login/login.html')

                # Authenticated old user, create a new one
                User.objects.create_user(username(request.POST['email']), password=request.POST['password'])
                user = authenticate(username=username(request.POST['email']), password=request.POST['password'])
                profile = Profile(user=user, memberid=old_member.memberid)
                profile.save()

                # Update the email on this actor, in case it were to differ from the sherpa2 email
                actor = profile.get_actor()
                actor.email = request.POST['email']
                actor.save()

                log_user_in(request, user)
                return HttpResponseRedirect(request.GET.get('next', reverse('user.views.home_new')))
            else:
                messages.error(request, 'invalid_credentials')
                context = {'next': request.GET.get('next')}
                return render(request, 'common/user/login/login.html', context)

def logout(request):
    log_user_out(request)
    return HttpResponseRedirect(reverse('page.views.page'))

def register(request):
    if request.method == 'GET':
        context = {
            'user_password_length': settings.USER_PASSWORD_LENGTH,
            'memberid_lookups_limit': settings.MEMBERID_LOOKUPS_LIMIT
        }
        return render(request, 'common/user/login/registration.html', context)
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
            if memberid_lookups_exceeded(request.META['REMOTE_ADDR']):
                messages.error(request, 'memberid_lookups_exceeded')
                return HttpResponseRedirect(reverse('user.login.views.register'))
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

            actor.email = request.POST['email']
            actor.save()
            user = User.objects.create_user(username(actor.email), password=request.POST['password'])
            profile = Profile(user=user, memberid=actor.memberid)
            profile.save()
            log_user_in(request, authenticate(username=user.username, password=request.POST['password']))
            t = loader.get_template('common/user/login/registered_email.html')
            c = RequestContext(request)
            send_mail(EMAIL_REGISTERED_SUBJECT, t.render(c), settings.DEFAULT_FROM_EMAIL, [profile.get_email()])
            return HttpResponseRedirect(reverse('user.views.home_new'))
        except (Actor.DoesNotExist, ValueError):
            messages.error(request, 'invalid_memberid')
            return HttpResponseRedirect(reverse('user.login.views.register'))

def register_nonmember(request):
    if request.method == 'GET':
        user_data = {}
        if 'user.registration_nonmember_attempt' in request.session:
            user_data = request.session['user.registration_nonmember_attempt']
            del request.session['user.registration_nonmember_attempt']

        context = {
            'user_password_length': settings.USER_PASSWORD_LENGTH,
            'user_data': user_data
        }
        return render(request, 'common/user/login/registration_nonmember.html', context)
    elif request.method == 'POST':
        errors = False

        # Check that name is provided
        if not validator.name(request.POST['name']):
            messages.error(request, 'invalid_name')
            errors = True

        # Check that the email address is valid
        if not validator.email(request.POST['email']):
            messages.error(request, 'invalid_email')
            errors = True

        # Check that the email address isn't in use
        if User.objects.filter(username=username(request.POST['email'])).exists():
            # Note! This COULD be a collision based on our username-algorithm (and pigs COULD fly)
            messages.error(request, 'email_exists')
            errors = True

        # Check that the password is long enough
        if len(request.POST['password']) < settings.USER_PASSWORD_LENGTH:
            messages.error(request, 'too_short_password')
            errors = True

        if errors:
            request.session['user.registration_nonmember_attempt'] = {
                'name': request.POST['name'],
                'email': request.POST['email']}
            return HttpResponseRedirect(reverse('user.login.views.register_nonmember'))

        user = User.objects.create_user(
            username(request.POST['email']),
            email=request.POST['email'],
            password=request.POST['password'])
        user.first_name = ' '.join(request.POST['name'].split(' ')[:-1])
        user.last_name = request.POST['name'].split(' ')[-1]
        user.save()
        profile = Profile(user=user)
        profile.save()
        log_user_in(request, authenticate(username=user.username, password=request.POST['password']))
        t = loader.get_template('common/user/login/registered_nonmember_email.html')
        c = RequestContext(request)
        send_mail(EMAIL_REGISTERED_SUBJECT, t.render(c), settings.DEFAULT_FROM_EMAIL, [profile.get_email()])
        return HttpResponseRedirect(reverse('user.views.home_new'))

def verify_memberid(request):
    if memberid_lookups_exceeded(request.META['REMOTE_ADDR']):
        return HttpResponse(json.dumps({'memberid_lookups_exceeded': True}))
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
    if not validator.email(request.POST['email']):
        return HttpResponse(json.dumps({'status': 'invalid_email'}))
    try:
        # Try users that aren't members first - this won't be many
        profile = User.objects.get(email=request.POST['email']).get_profile()
    except User.DoesNotExist:
        try:
            actor = Actor.objects.get(email=request.POST['email'])
            profile = Profile.objects.get(memberid=actor.memberid)
        except Actor.DoesNotExist:
            return HttpResponse(json.dumps({'status': 'unknown_email'}))
        except Profile.DoesNotExist:
            # This means the email exists in Focus, but the user isn't in our user-base.
            # Maybe we should inform them that they're not registered, or something?
            return HttpResponse(json.dumps({'status': 'unknown_email'}))
        except Actor.MultipleObjectsReturned:
            # TODO: Multiple email-hits will need to be handled differently soon
            return HttpResponse(json.dumps({'status': 'multiple_hits'}))
    except KeyError:
        return HttpResponse(json.dumps({'status': 'unknown_email'}))
    key = crypto.get_random_string(length=settings.RESTORE_PASSWORD_KEY_LENGTH)
    profile.password_restore_key = key
    profile.password_restore_date = datetime.now()
    profile.save()
    t = loader.get_template('common/user/login/restore-password-email.html')
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
        return render(request, 'common/user/login/restore-password.html', context)
    deadline = profile.password_restore_date + timedelta(hours=settings.RESTORE_PASSWORD_VALIDITY)
    if datetime.now() > deadline:
        # We've passed the deadline for key validity
        context = {'key_expired': True, 'validity_period': settings.RESTORE_PASSWORD_VALIDITY}
        return render(request, 'common/user/login/restore-password.html', context)

    # Passed all tests, looks like we're ready to reset the password
    if request.method == 'GET':
        context = {'ready': True, 'key': key, 'password_length': settings.USER_PASSWORD_LENGTH}
        return render(request, 'common/user/login/restore-password.html', context)
    elif request.method == 'POST':
        if request.POST['password'] != request.POST['password-duplicate'] or len(request.POST['password']) < settings.USER_PASSWORD_LENGTH:
            context = {'ready': True, 'key': key, 'password_length': settings.USER_PASSWORD_LENGTH,
                'unacceptable_password': True}
            return render(request, 'common/user/login/restore-password.html', context)
        # Everything is in order. Reset the password.
        profile.user.set_password(request.POST['password'])
        profile.user.save()
        profile.password_restore_key = None
        profile.password_restore_date = None
        profile.save()
        context = {'success': True}
        return render(request, 'common/user/login/restore-password.html', context)
