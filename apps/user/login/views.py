# encoding: utf-8
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login as log_user_in, logout as log_user_out
from django.contrib import messages
from django.template import RequestContext, loader
from django.utils import crypto
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist

from datetime import datetime, timedelta
from smtplib import SMTPException
import json
import logging
import sys
import hashlib

from user.models import User
from user.util import memberid_lookups_exceeded
from user.login.util import attempt_login
from focus.models import Actor, Enrollment
from focus.util import get_enrollment_email_matches
from core import validator
from core.models import FocusCountry
from sherpa25.models import Member
from connect.util import add_signon_session_value

EMAIL_REGISTERED_SUBJECT = u"Velkommen som bruker på DNTs nettsted"
EMAIL_REGISTERED_NONMEMBER_SUBJECT = EMAIL_REGISTERED_SUBJECT

logger = logging.getLogger('sherpa')

def login(request):
    if 'authenticated_users' in request.session:
        del request.session['authenticated_users']

    context = {
        'user_password_length': settings.USER_PASSWORD_LENGTH,
        'memberid_lookups_limit': settings.MEMBERID_LOOKUPS_LIMIT,
        'countries': FocusCountry.get_sorted(),
    }

    if request.method == 'GET':
        if request.user.is_authenticated():
            # User is already authenticated, skip login
            return redirect(request.GET.get('next', reverse('user.views.home')))

        if 'registreringsnokkel' in request.GET:
            try:
                user = User.get_users(include_pending=True).get(pending_registration_key=request.GET['registreringsnokkel'])
                context['user_to_register'] = user
            except User.DoesNotExist:
                pass

        context['next'] = request.GET.get('next')
        return render(request, 'common/user/login/login.html', context)

    elif request.method == 'POST':
        matches, message = attempt_login(request)

        if len(matches) == 1:
            return redirect(request.GET.get('next', reverse('user.views.home')))

        elif len(matches) > 1:
            # Multiple matches, offer a choice between all matches
            request.session['authenticated_users'] = [u.id for u in matches]
            if 'next' in request.GET:
                return redirect("%s?next=%s" %
                    (reverse('user.login.views.choose_authenticated_user'), request.GET['next']))
            else:
                return redirect('user.login.views.choose_authenticated_user')

        else:
            messages.error(request, message)
            context['next'] = request.GET.get('next')
            context['email'] = request.POST['email']
            return render(request, 'common/user/login/login.html', context)

    else:
        return redirect('user.login.views.login')

def choose_authenticated_user(request):
    if not 'authenticated_users' in request.session:
        return redirect('user.login.views.login')

    users = User.get_users(include_pending=True).filter(id__in=request.session['authenticated_users'], is_active=True)
    context = {
        'users': sorted(users, key=lambda u: u.get_first_name()),
        'next': request.GET.get('next')
    }
    return render(request, 'common/user/login/choose_authenticated_user.html', context)

def login_chosen_user(request):
    if not 'authenticated_users' in request.session:
        return redirect('user.login.views.login')

    if not 'user' in request.POST:
        del request.session['authenticated_users']
        return redirect('user.login.views.login')

    # Verify that the user authenticated for this user
    if not int(request.POST['user']) in request.session['authenticated_users']:
        del request.session['authenticated_users']
        return redirect('user.login.views.login')

    # All is swell, log the user in
    user = User.get_users(include_pending=True).get(id=request.POST['user'], is_active=True)
    user = authenticate(user=user)
    log_user_in(request, user)
    if 'dntconnect' in request.session:
        add_signon_session_value(request, 'logget_inn')
    del request.session['authenticated_users']
    return redirect(request.GET.get('next', reverse('user.views.home')))

def logout(request):
    log_user_out(request)
    return redirect('page.views.page')

def register(request):
    if request.method == 'POST':
        try:
            # Check that the password is long enough
            if len(request.POST['password']) < settings.USER_PASSWORD_LENGTH:
                messages.error(request, 'too_short_password')
                return redirect("%s#registrering" % reverse('user.login.views.login'))

            # Check that the email address is valid
            if not validator.email(request.POST['email']):
                messages.error(request, 'invalid_email')
                return redirect("%s#registrering" % reverse('user.login.views.login'))

            # Check that the memberid is correct (and retrieve the Actor-entry)
            if memberid_lookups_exceeded(request.META['REMOTE_ADDR']):
                messages.error(request, 'memberid_lookups_exceeded')
                return redirect("%s#registrering" % reverse('user.login.views.login'))
            if not FocusCountry.objects.filter(code=request.POST['country']).exists():
                raise PermissionDenied
            actor = Actor.objects.filter(
                memberid=request.POST['memberid'],
                address__country_code=request.POST['country'])
            if request.POST['country'] == 'NO':
                actor = actor.filter(address__zipcode=request.POST['zipcode'])
            if actor.exists():
                actor = actor.get()
            else:
                # No matching actors, check for pending users
                enrollment = Enrollment.get_active().filter(memberid=request.POST['memberid'])
                if request.POST['country'] == 'NO':
                    enrollment = enrollment.filter(zipcode=request.POST['zipcode'])
                if enrollment.exists():
                    actor = User.get_users(include_pending=True).get(memberid=request.POST['memberid'])
                else:
                    # Give up
                    raise ObjectDoesNotExist

            # Check that the user doesn't already have an account
            if User.get_users(include_pending=True).filter(memberid=request.POST['memberid'], is_active=True).exists():
                messages.error(request, 'user_exists')
                return redirect("%s#registrering" % reverse('user.login.views.login'))

            # Check that the memberid isn't expired.
            # Expired memberids shouldn't exist in Focus, so this is an error and should never happen,
            # but we'll check for it anyway.
            if User.objects.filter(memberid=request.POST['memberid'], is_expired=True).exists():
                messages.error(request, 'expired_user_exists')
                return redirect("%s#registrering" % reverse('user.login.views.login'))

            actor.set_email(request.POST['email'].strip())

            try:
                # Check if the user's already created as inactive
                user = User.get_users(include_pending=True).get(memberid=request.POST['memberid'], is_active=False)
                user.is_active = True
                user.set_password(request.POST['password'])
                user.save()
            except User.DoesNotExist:
                # New user
                user = User(identifier=actor.memberid, memberid=actor.memberid)
                user.set_password(request.POST['password'])
                user.save()

            authenticate(user=user)
            log_user_in(request, user)
            if 'dntconnect' in request.session:
                if 'innmelding.aktivitet' in request.session:
                    add_signon_session_value(request, 'innmeldt')
                else:
                    add_signon_session_value(request, 'registrert')
            t = loader.get_template('common/user/login/registered_email.html')
            c = RequestContext(request)
            send_mail(EMAIL_REGISTERED_SUBJECT, t.render(c), settings.DEFAULT_FROM_EMAIL, [user.get_email()])
            return redirect(request.GET.get('next', reverse('user.views.home')))
        except (ObjectDoesNotExist, ValueError):
            messages.error(request, 'invalid_memberid')
            return redirect("%s#registrering" % reverse('user.login.views.login'))
        except SMTPException:
            # Silently log and ignore this error. Consider warning the user that the email wasn't sent?
            logger.warning(u"Klarte ikke å sende registreringskvitteringepost",
                exc_info=sys.exc_info(),
                extra={'request': request}
            )
            return redirect('user.views.home')
    else:
        return redirect('user.login.views.login')

def register_nonmember(request):
    if request.method == 'GET':
        user_data = {}
        if 'user.registration_nonmember_attempt' in request.session:
            user_data = request.session['user.registration_nonmember_attempt']
            del request.session['user.registration_nonmember_attempt']

        context = {
            'user_password_length': settings.USER_PASSWORD_LENGTH,
            'user_data': user_data,
            'next': request.GET.get('next'),
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
        if User.objects.filter(identifier=request.POST['email']).exists():
            messages.error(request, 'email_exists')
            errors = True

        # Check that the password is long enough
        if len(request.POST['password']) < settings.USER_PASSWORD_LENGTH:
            messages.error(request, 'too_short_password')
            errors = True

        if errors:
            request.session['user.registration_nonmember_attempt'] = {
                'name': request.POST['name'],
                'email': request.POST['email']
            }
            return redirect('user.login.views.register_nonmember')

        user = User(identifier=request.POST['email'], email=request.POST['email'])
        user.first_name, user.last_name = request.POST['name'].rsplit(' ', 1)
        user.set_password(request.POST['password'])
        user.save()
        authenticate(user=user)
        log_user_in(request, user)
        if 'dntconnect' in request.session:
            add_signon_session_value(request, 'registrert')
        t = loader.get_template('common/user/login/registered_nonmember_email.html')
        c = RequestContext(request)
        send_mail(EMAIL_REGISTERED_SUBJECT, t.render(c), settings.DEFAULT_FROM_EMAIL, [user.get_email()])
        return redirect(request.GET.get('next', reverse('user.views.home')))

def verify_memberid(request):
    if memberid_lookups_exceeded(request.META['REMOTE_ADDR']):
        return HttpResponse(json.dumps({'memberid_lookups_exceeded': True}))
    if not FocusCountry.objects.filter(code=request.POST['country']).exists():
        raise PermissionDenied
    try:
        actor = Actor.objects.filter(
            memberid=request.POST['memberid'],
            address__country_code=request.POST['country'])
        if request.POST['country'] == 'NO':
            actor = actor.filter(address__zipcode=request.POST['zipcode'])
        if actor.exists():
            actor = actor.get()
        else:
            # No matching actors, check for pending users
            enrollment = Enrollment.get_active().filter(memberid=request.POST['memberid'])
            if request.POST['country'] == 'NO':
                enrollment = enrollment.filter(zipcode=request.POST['zipcode'])
            if enrollment.exists():
                actor = User.get_users(include_pending=True).get(memberid=request.POST['memberid'])
            else:
                # Give up
                raise ObjectDoesNotExist

        try:
            user = User.objects.get(memberid=request.POST['memberid'], is_active=True)
            user_exists = True
            user_is_expired = user.is_expired
        except User.DoesNotExist:
            user_exists = False
            user_is_expired = False

        return HttpResponse(json.dumps({
            'exists': True,
            'name': actor.get_full_name(),
            'email': actor.get_email(),
            'user_exists': user_exists,
            'user_is_expired': user_is_expired
        }))
    except (ValueError, ObjectDoesNotExist):
        return HttpResponse(json.dumps({'exists': False}))

def send_restore_password_email(request):
    if not validator.email(request.POST['email']):
        return HttpResponse(json.dumps({'status': 'invalid_email'}))

    # The address will match only one non-member, but may match several members, registered or not
    local_matches = list(User.objects.filter(email=request.POST['email']))
    focus_unregistered_matches = False
    for a in Actor.objects.filter(email=request.POST['email']):
        try:
            # Include pending users in case they're resetting it *after* verification (i.e. Actor created),
            # but *before* we've checked if they should still be pending.
            local_matches.append(User.get_users(include_pending=True).get(memberid=a.memberid, is_active=True))
        except User.DoesNotExist:
            focus_unregistered_matches = True

    for e in get_enrollment_email_matches(request.POST['email']):
        try:
            local_matches.append(User.get_users(include_pending=True).get(memberid=e.memberid, is_pending=True, is_active=True))
        except User.DoesNotExist:
            pass

    # Check for matching old user system members - we'll generate a password so that they can login and be imported
    all_sherpa2_matches = Member.objects.filter(email=request.POST['email'])
    # Include expired users when excluding sherpa2 matches - if their current user object is expired,
    # it's irrelevant whether or not the old user account matches
    sherpa2_matches = [m for m in all_sherpa2_matches if not User.objects.filter(memberid=m.memberid, is_active=True).exists()]

    if len(local_matches) == 0 and len(sherpa2_matches) == 0:
        # No email-address matches.
        if focus_unregistered_matches:
            # Oh, the email address exists in Focus, but the user(s) aren't in our user-base. Let them know.
            return HttpResponse(json.dumps({'status': 'unregistered_email'}))
        else:
            return HttpResponse(json.dumps({'status': 'unknown_email'}))

    if len(sherpa2_matches) > 0:
        for member in sherpa2_matches:
            sha1 = hashlib.sha1()
            new_password = crypto.get_random_string(length=10)
            sha1.update(new_password)
            member.password = sha1.hexdigest()
            member.save()

        t = loader.get_template('common/user/login/restore-password-email-sherpa25.txt')
        c = RequestContext(request, {
            'member': member,
            'new_password': new_password
        })
        send_mail("Nytt passord på Min side", t.render(c), settings.DEFAULT_FROM_EMAIL, [request.POST['email']])

    if len(local_matches) > 0:
        for user in local_matches:
            key = crypto.get_random_string(length=settings.RESTORE_PASSWORD_KEY_LENGTH)
            while User.objects.filter(password_restore_key=key).exists():
                # Ensure that the key isn't already in use. With the current key length of 40, we'll have
                # ~238 bits of entropy which means that this will never ever happen, ever.
                # You will win the lottery before this happens. And I want to know if it does, so log it.
                logger.warning(u"Noen fikk en random-generert password-restore-key som allerede finnes!",
                    exc_info=sys.exc_info(),
                    extra={
                        'request': request,
                        'should_you_play_the_lottery': True,
                        'key': key
                    }
                )
                key = crypto.get_random_string(length=settings.RESTORE_PASSWORD_KEY_LENGTH)

            user.password_restore_key = key
            user.password_restore_date = datetime.now()
            user.save()

        if len(local_matches) == 1:
            t = loader.get_template('common/user/login/restore-password-email.txt')
            c = RequestContext(request, {
                'found_user': user,
                'validity_period': settings.RESTORE_PASSWORD_VALIDITY
            })
        else:
            t = loader.get_template('common/user/login/restore-password-email-multiple.txt')
            c = RequestContext(request, {
                'users': local_matches,
                'validity_period': settings.RESTORE_PASSWORD_VALIDITY
            })
        send_mail("Nytt passord på Min side", t.render(c), settings.DEFAULT_FROM_EMAIL, [request.POST['email']])
    return HttpResponse(json.dumps({'status': 'success'}))

def restore_password(request, key):
    users = User.get_users(include_pending=True).filter(password_restore_key=key, is_active=True)
    if len(users) == 0:
        context = {
            'no_such_key': True,
            'user_password_length': settings.USER_PASSWORD_LENGTH
        }
        return render(request, 'common/user/login/restore-password.html', context)

    date_limit = datetime.now() - timedelta(hours=settings.RESTORE_PASSWORD_VALIDITY)
    if any([u.password_restore_date < date_limit for u in users]):
        # We've passed the deadline for key validity
        context = {
            'key_expired': True,
            'validity_period': settings.RESTORE_PASSWORD_VALIDITY,
            'user_password_length': settings.USER_PASSWORD_LENGTH
        }
        return render(request, 'common/user/login/restore-password.html', context)

    # Passed all tests, looks like we're ready to reset the password
    if request.method == 'GET':
        context = {
            'ready': True,
            'key': key,
            'user_password_length': settings.USER_PASSWORD_LENGTH
        }
        return render(request, 'common/user/login/restore-password.html', context)
    elif request.method == 'POST':
        if request.POST['password'] != request.POST['password-repeat'] or len(request.POST['password']) < settings.USER_PASSWORD_LENGTH:
            context = {
                'ready': True,
                'key': key,
                'user_password_length': settings.USER_PASSWORD_LENGTH,
                'unacceptable_password': True
            }
            return render(request, 'common/user/login/restore-password.html', context)

        # Everything is in order. Reset the password.
        for user in users:
            user.set_password(request.POST['password'])
            user.password_restore_key = None
            user.password_restore_date = None
            user.save()

        # Log the user in automatically
        user = authenticate(user=user)
        log_user_in(request, user)
        messages.info(request, 'password_reset_success')
        return redirect('user.views.home')
