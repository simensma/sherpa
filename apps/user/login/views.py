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
import json
import logging
import hashlib

from user.models import User
from user.util import memberid_lookups_exceeded
from user.login.util import attempt_login, attempt_registration, attempt_registration_nonmember
from focus.models import Actor, Enrollment
from focus.util import get_enrollment_email_matches
from core import validator
from core.models import FocusCountry
from sherpa25.models import Member

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
                context['prefilled_user'] = user
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

    users = User.get_users(include_pending=True).filter(id__in=request.session['authenticated_users'], is_inactive=False)
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
    user = User.get_users(include_pending=True).get(id=request.POST['user'], is_inactive=False)
    user = authenticate(user=user)
    log_user_in(request, user)
    del request.session['authenticated_users']
    return redirect(request.GET.get('next', reverse('user.views.home')))

def logout(request):
    log_user_out(request)
    return redirect('page.views.page')

def register(request):
    if request.method != 'POST':
        return redirect('user.login.views.login')
    else:
        user, message = attempt_registration(request)
        if user is None:
            messages.error(request, message)
            return redirect("%s#registrering" % reverse('user.login.views.login'))
        else:
            return redirect(request.GET.get('next', reverse('user.views.home')))

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
        user, error_messages = attempt_registration_nonmember(request)

        if user is None:
            for message in error_messages:
                messages.error(request, message)

            request.session['user.registration_nonmember_attempt'] = {
                'name': request.POST['name'],
                'email': request.POST['email']
            }
            return redirect('user.login.views.register_nonmember')
        else:
            return redirect(request.GET.get('next', reverse('user.views.home')))

def verify_memberid(request):
    if not all([q in request.POST for q in ['country', 'memberid', 'zipcode']]):
        # Some clients seem to send empty query dicts, see e.g.:
        # https://sentry.turistforeningen.no/turistforeningen/sherpa/group/1173/
        raise PermissionDenied
    if memberid_lookups_exceeded(request.META['REMOTE_ADDR']):
        return HttpResponse(json.dumps({'memberid_lookups_exceeded': True}))
    if not FocusCountry.objects.filter(code=request.POST['country']).exists():
        raise PermissionDenied
    try:
        # Not filtering on Actor.get_members(), see below
        actor = Actor.objects.filter(
            memberid=request.POST['memberid'],
            address__country_code=request.POST['country']
        )
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

        # Check that it's a proper member object (note that we didn't filter the query on Actor.get_members())
        if not actor.is_member():
            return HttpResponse(json.dumps({
                'actor_is_not_member': True,
            }))

        try:
            user = User.objects.get(memberid=request.POST['memberid'], is_inactive=False)
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
    if not 'email' in request.POST:
        raise PermissionDenied

    if not validator.email(request.POST['email']):
        return HttpResponse(json.dumps({'status': 'invalid_email'}))

    # The address will match only one non-member, but may match several members, registered or not
    local_matches = list(User.objects.filter(email=request.POST['email']))
    focus_unregistered_matches = False
    for a in Actor.get_members().filter(email=request.POST['email']):
        try:
            # Include pending users in case they're resetting it *after* verification (i.e. Actor created),
            # but *before* we've checked if they should still be pending.
            local_matches.append(User.get_users(include_pending=True).get(memberid=a.memberid, is_inactive=False))
        except User.DoesNotExist:
            focus_unregistered_matches = True

    for e in get_enrollment_email_matches(request.POST['email']):
        try:
            local_matches.append(User.get_users(include_pending=True).get(memberid=e.memberid, is_pending=True, is_inactive=False))
        except User.DoesNotExist:
            pass

    # Check for matching old user system members - we'll generate a password so that they can login and be imported
    all_sherpa2_matches = Member.objects.filter(email=request.POST['email'])
    # Include expired users when excluding sherpa2 matches - if their current user object is expired,
    # it's irrelevant whether or not the old user account matches
    sherpa2_matches = [m for m in all_sherpa2_matches if not User.objects.filter(memberid=m.memberid, is_inactive=False).exists()]

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
    users = User.get_users(include_pending=True).filter(password_restore_key=key, is_inactive=False)
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
