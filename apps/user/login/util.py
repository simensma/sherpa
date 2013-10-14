# encoding: utf-8
from django.contrib.auth import authenticate, login as log_user_in
from django.conf import settings
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.template import RequestContext, loader
from django.core.mail import send_mail

from smtplib import SMTPException
import logging
import sys

from core.models import FocusCountry
from user.models import User
from user.util import authenticate_sherpa2_user, authenticate_users
from focus.models import Actor, Enrollment
from sherpa25.models import import_fjelltreffen_annonser
from core import validator
from user.util import memberid_lookups_exceeded

EMAIL_REGISTERED_SUBJECT = u"Velkommen som bruker på DNTs nettsted"

logger = logging.getLogger('sherpa')

def attempt_login(request):
    matches = authenticate_users(request.POST['email'], request.POST['password'])

    if len(matches) == 1:
        # Exactly one match, cool, just authenticate the user
        user = authenticate(user=matches[0])
        log_user_in(request, user)
        return matches, None

    elif len(matches) > 1:
        # Multiple matches, let the caller handle this
        return matches, None

    elif len(matches) == 0:
        # Incorrect credentials. Check if this is a user from the old userpage system
        old_member = authenticate_sherpa2_user(request.POST['email'], request.POST['password'])
        if old_member is not None:
            # Actually, it is! Let's try to import them.
            if User.get_users().filter(memberid=old_member.memberid, is_active=True).exists():
                return matches, 'old_memberid_but_memberid_exists'

            # Check if a pending user exists. This shouldn't ever happen (a pending user is recently
            # enrolled, and an existing user will have been member for a long time).
            if User.objects.filter(memberid=old_member.memberid, is_pending=True).exists():
                # Give the same error ("user exists, you need to use your new password")
                return matches, 'old_memberid_but_memberid_exists'

            # Verify that they exist in the membersystem (this turned out to be an incorrect assumption)
            if not Actor.objects.filter(memberid=old_member.memberid).exists():
                # We're not quite sure why this can happen, so we'll just give them the invalid
                # credentials message - but this might be confusing for those who were able to log
                # in previously.
                return matches, 'invalid_credentials'

            # Create the new user
            try:
                # Check if the user's already created as inactive
                user = User.get_users().get(memberid=old_member.memberid, is_active=False)
                user.is_active = True
                user.set_password(request.POST['password'])
                user.save()
            except User.DoesNotExist:
                # New user
                user = User(identifier=old_member.memberid, memberid=old_member.memberid)
                user.set_password(request.POST['password'])
                user.save()

            # Update the email on this actor, in case it were to differ from the sherpa2 email
            user.update_personal_data({'email': request.POST['email']})

            # Import any fjelltreffen-annonser from the old system
            import_fjelltreffen_annonser(user)

            authenticate(user=user)
            log_user_in(request, user)
            return [user], None

        else:
            # No luck, just provide the error message
            return matches, 'invalid_credentials'

def attempt_registration(request):
    try:
        # Check that the password is long enough
        if len(request.POST['password']) < settings.USER_PASSWORD_LENGTH:
            return None, 'too_short_password'

        # Check that the email address is valid
        if not validator.email(request.POST['email']):
            return None, 'invalid_email'

        # Check that the memberid is correct (and retrieve the Actor-entry)
        if memberid_lookups_exceeded(request.META['REMOTE_ADDR']):
            return None, 'memberid_lookups_exceeded'
        if not FocusCountry.objects.filter(code=request.POST['country']).exists():
            raise PermissionDenied
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

        # Check that the user doesn't already have an account
        if User.get_users(include_pending=True).filter(memberid=request.POST['memberid'], is_active=True).exists():
            return None, 'user_exists'

        # Check that the memberid isn't expired.
        # Expired memberids shouldn't exist in Focus, so this is an error and should never happen,
        # but we'll check for it anyway.
        if User.objects.filter(memberid=request.POST['memberid'], is_expired=True).exists():
            return None, 'expired_user_exists'

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

        try:
            t = loader.get_template('common/user/login/registered_email.txt')
            c = RequestContext(request)
            send_mail(EMAIL_REGISTERED_SUBJECT, t.render(c), settings.DEFAULT_FROM_EMAIL, [user.get_email()])
        except SMTPException:
            # Silently log and ignore this error. Consider warning the user that the email wasn't sent?
            logger.warning(u"Klarte ikke å sende registreringskvitteringepost",
                exc_info=sys.exc_info(),
                extra={'request': request}
            )

        return user, None

    except (ObjectDoesNotExist, ValueError):
        return None, 'invalid_memberid'

def attempt_registration_nonmember(request):
    error_messages = []

    # Check that name is provided
    if not validator.name(request.POST['name']):
        error_messages.append('invalid_name')

    # Check that the email address is valid
    if not validator.email(request.POST['email']):
        error_messages.append('invalid_email')

    # Check that the email address isn't in use
    if User.objects.filter(identifier=request.POST['email']).exists():
        error_messages.append('email_exists')

    # Check that the password is long enough
    if len(request.POST['password']) < settings.USER_PASSWORD_LENGTH:
        error_messages.append('too_short_password')

    if len(error_messages) > 0:
        request.session['user.registration_nonmember_attempt'] = {
            'name': request.POST['name'],
            'email': request.POST['email']
        }
        return None, error_messages

    user = User(identifier=request.POST['email'], email=request.POST['email'])
    user.first_name, user.last_name = request.POST['name'].rsplit(' ', 1)
    user.set_password(request.POST['password'])
    user.save()
    authenticate(user=user)
    log_user_in(request, user)

    try:
        t = loader.get_template('common/user/login/registered_nonmember_email.txt')
        c = RequestContext(request)
        send_mail(EMAIL_REGISTERED_SUBJECT, t.render(c), settings.DEFAULT_FROM_EMAIL, [user.get_email()])
    except SMTPException:
        # Silently log and ignore this error. Consider warning the user that the email wasn't sent?
        logger.warning(u"Klarte ikke å sende registreringskvitteringepost",
            exc_info=sys.exc_info(),
            extra={'request': request}
        )

    return user, None
