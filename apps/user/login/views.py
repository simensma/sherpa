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
from django.core.exceptions import PermissionDenied

from datetime import datetime, timedelta
from smtplib import SMTPException
import json
import logging
import sys
import hashlib

from user.models import User
from focus.models import Actor
from user.util import memberid_lookups_exceeded, authenticate_sherpa2_user, authenticate_users
from core import validator
from core.models import FocusCountry
from sherpa25.models import Member, import_fjelltreffen_annonser

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
        context['next'] = request.GET.get('next')
        return render(request, 'common/user/login/login.html', context)

    elif request.method == 'POST':
        matches = authenticate_users(request.POST['email'], request.POST['password'])

        if len(matches) == 1:
            # Exactly one match, cool, just authenticate the user
            user = authenticate(user=matches[0])
            log_user_in(request, user)
            return redirect(request.GET.get('next', reverse('user.views.home')))

        elif len(matches) > 1:
            # Multiple matches, offer a choice between all matches
            request.session['authenticated_users'] = [u.id for u in matches]
            if 'next' in request.GET:
                return redirect("%s?next=%s" %
                    (reverse('user.login.views.choose_authenticated_user'), request.GET['next']))
            else:
                return redirect('user.login.views.choose_authenticated_user')

        elif len(matches) == 0:
            # Incorrect credentials. Check if this is a user from the old userpage system
            old_member = authenticate_sherpa2_user(request.POST['email'], request.POST['password'])
            if old_member is not None:
                # Actually, it is! Let's try to import them.
                if User.objects.filter(memberid=old_member.memberid, is_active=True).exists():
                    messages.error(request, 'old_memberid_but_memberid_exists')
                    context['email'] = request.POST['email']
                    return render(request, 'common/user/login/login.html', context)

                # Verify that they exist in the membersystem (this turned out to be an incorrect assumption)
                if not Actor.objects.filter(memberid=old_member.memberid).exists():
                    # We're not quite sure why this can happen, so we'll just give them the invalid
                    # credentials message - but this might be confusing for those who were able to log
                    # in previously.
                    messages.error(request, 'invalid_credentials')
                    context['next'] = request.GET.get('next')
                    context['email'] = request.POST['email']
                    return render(request, 'common/user/login/login.html', context)

                # Create the new user
                try:
                    # Check if the user's already created as inactive
                    user = User.objects.get(memberid=old_member.memberid, is_active=False)
                    user.is_active = True
                    user.set_password(request.POST['password'])
                    user.save()
                except User.DoesNotExist:
                    # New user
                    user = User(identifier=old_member.memberid, memberid=old_member.memberid)
                    user.set_password(request.POST['password'])
                    user.save()

                # Update the email on this actor, in case it were to differ from the sherpa2 email
                actor = user.get_actor()
                actor.email = request.POST['email']
                actor.save()

                # Import any fjelltreffen-annonser from the old system
                import_fjelltreffen_annonser(user)

                authenticate(user=user)
                log_user_in(request, user)
                return redirect(request.GET.get('next', reverse('user.views.home')))

            else:
                # No luck, just provide the error message
                messages.error(request, 'invalid_credentials')
                context['next'] = request.GET.get('next')
                context['email'] = request.POST['email']
                return render(request, 'common/user/login/login.html', context)
    else:
        return redirect('user.login.views.login')

def choose_authenticated_user(request):
    if not 'authenticated_users' in request.session:
        return redirect('user.login.views.login')

    users = User.objects.filter(id__in=request.session['authenticated_users'], is_active=True)
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
    user = User.objects.get(id=request.POST['user'], is_active=True)
    user = authenticate(user=user)
    log_user_in(request, user)
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
            actor = actor.get()

            # Check that the user doesn't already have an account
            if User.objects.filter(memberid=request.POST['memberid'], is_active=True).exists():
                messages.error(request, 'user_exists')
                return redirect("%s#registrering" % reverse('user.login.views.login'))

            actor.email = request.POST['email']
            actor.save()

            try:
                # Check if the user's already created as inactive
                user = User.objects.get(memberid=request.POST['memberid'], is_active=False)
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
            t = loader.get_template('common/user/login/registered_email.html')
            c = RequestContext(request)
            send_mail(EMAIL_REGISTERED_SUBJECT, t.render(c), settings.DEFAULT_FROM_EMAIL, [user.get_email()])
            return redirect('user.views.home')
        except (Actor.DoesNotExist, ValueError):
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
        t = loader.get_template('common/user/login/registered_nonmember_email.html')
        c = RequestContext(request)
        send_mail(EMAIL_REGISTERED_SUBJECT, t.render(c), settings.DEFAULT_FROM_EMAIL, [user.get_email()])
        return redirect('user.views.home')

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
        actor = actor.get()
        return HttpResponse(json.dumps({
            'exists': True,
            'name': actor.get_full_name(),
            'email': actor.email or '',
            'user_exists': User.objects.filter(memberid=request.POST['memberid'], is_active=True).exists()
        }))
    except (ValueError, Actor.DoesNotExist):
        return HttpResponse(json.dumps({'exists': False}))

def send_restore_password_email(request):
    if not validator.email(request.POST['email']):
        return HttpResponse(json.dumps({'status': 'invalid_email'}))

    # The address will match only one non-member, but may match several members, registered or not
    local_matches = list(User.objects.filter(email=request.POST['email']))
    focus_unregistered_matches = False
    for a in Actor.objects.filter(email=request.POST['email']):
        try:
            local_matches.append(User.objects.get(memberid=a.memberid, is_active=True))
        except User.DoesNotExist:
            focus_unregistered_matches = True

    # Check for matching old user system members - we'll generate a password so that they can login and be imported
    all_sherpa2_matches = Member.objects.filter(email=request.POST['email'])
    sherpa2_matches = [m for m in all_sherpa2_matches if not User.objects.filter(memberid=m.memberid, is_active=True).exists()]

    if len(local_matches) == 0 and len(sherpa2_matches) == 0:
        # No email-address matches.
        if focus_unregistered_matches:
            # Oh, the email address exists in Focus, but the user(s) aren't in our user-base. Let them know.
            return HttpResponse(json.dumps({'status': 'unregistered_email'}))
        else:
            return HttpResponse(json.dumps({'status': 'unknown_email'}))

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
            user.password_restore_key = key
            user.password_restore_date = datetime.now()
            user.save()

        t = loader.get_template('common/user/login/restore-password-email.txt')
        c = RequestContext(request, {
            'found_user': user,
            'validity_period': settings.RESTORE_PASSWORD_VALIDITY})
        send_mail("Nytt passord på Min side", t.render(c), settings.DEFAULT_FROM_EMAIL, [request.POST['email']])
    return HttpResponse(json.dumps({'status': 'success'}))

def restore_password(request, key):
    users = User.objects.filter(password_restore_key=key, is_active=True)
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

def connect_signon(request):
    if not 'dntconnect' in request.session:
        # Use a friendlier error message here?
        raise PermissionDenied

    context = {'client_name': request.session['dntconnect']['client']['friendly_name']}
    return render(request, 'common/user/login/connect-signon.html', context)
