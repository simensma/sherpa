# encoding: utf-8
from datetime import datetime, timedelta
import json
import logging
import hashlib

from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login as log_user_in, logout as log_user_out
from django.contrib import messages
from django.template import RequestContext, loader
from django.utils import crypto
from django.core.exceptions import PermissionDenied

from user.models import User
from user.util import verify_memberid as verify_memberid_util
from user.login.util import attempt_login, attempt_registration, attempt_registration_nonmember
from user.exceptions import MemberidLookupsExceeded, CountryDoesNotExist, NoMatchingMemberid, ActorIsNotPersonalMember
from focus.models import Actor
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
        # Some clients seem to send empty query dicts
        raise PermissionDenied

    try:
        user = verify_memberid_util(
            ip_address=request.META['REMOTE_ADDR'],
            memberid=request.POST['memberid'],
            country_code=request.POST['country'],
            zipcode=request.POST['zipcode'],
        )

        return HttpResponse(json.dumps({
            'exists': True,
            'name': user.get_full_name(),
            'email': user.get_email(),
            'user_exists': not user.is_inactive,
        }))

    except MemberidLookupsExceeded:
        return HttpResponse(json.dumps({
            'memberid_lookups_exceeded': True,
        }))

    except CountryDoesNotExist:
        raise PermissionDenied

    except ActorIsNotPersonalMember:
        return HttpResponse(json.dumps({
            'actor_is_not_member': True,
        }))

    except (NoMatchingMemberid, ValueError):
        return HttpResponse(json.dumps({'exists': False}))

def send_restore_password_email(request):
    if not 'email' in request.POST:
        raise PermissionDenied

    if not validator.email(request.POST['email']):
        return HttpResponse(json.dumps({'status': 'invalid_email'}))

    # The address might match one non-member, check it:
    local_matches = list(User.objects.filter(memberid__isnull=True, email=request.POST['email']))

    # The address might match several members, registered or not
    focus_unregistered_matches = False

    # Search through matching Actors
    for actor in Actor.get_personal_members().filter(email=request.POST['email']):
        try:
            # Ok, look for any matching active user
            user = User.get_users(
                include_pending=True,
                include_expired=True
            ).get(
                memberid=actor.memberid,
                is_inactive=False # ignore inactive users; these need to register first
            )

            # Reset state if this user was previously pending but is now a proper member
            if user.is_pending:
                user.is_pending = False
                user.save()

            # Reset state if this user was previously marked as expired for some reason
            if user.is_expired:
                user.is_expired = False
                user.save()

            local_matches.append(user)
        except User.DoesNotExist:
            # There is an actor but no corresponding user - inform the user that they need to register
            focus_unregistered_matches = True

    # Now search through matching active enrollments
    for enrollment in get_enrollment_email_matches(request.POST['email']):
        try:
            # Ok, look for any matching active AND pending user
            user = User.get_users(
                include_pending=True,
                include_expired=True
            ).get(
                memberid=enrollment.memberid,
                is_pending=True,
                is_inactive=False # ignore inactive users; these need to register first
            )

            # Reset state if this user was previously marked as expired for some reason
            if user.is_expired:
                user.is_expired = False
                user.save()

            # Check that the user isn't already matched as an Actor since this theoretically could be a duplicate
            if user not in local_matches:
                local_matches.append(user)
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
