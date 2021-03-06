# encoding: utf-8
from smtplib import SMTPException
from ssl import SSLError
import logging
import sys

from django.contrib.auth import authenticate, login as log_user_in
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.template import RequestContext, loader
from django.core.mail import send_mail

from core import validator
from user.models import User
from user.util import authenticate_sherpa2_user, authenticate_users, verify_memberid
from user.exceptions import MemberidLookupsExceeded, CountryDoesNotExist, NoMatchingMemberid, ActorIsNotPersonalMember
from focus.models import Actor
from sherpa25.util import import_fjelltreffen_annonser

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
            if User.get_users().filter(memberid=old_member.memberid, is_inactive=False).exists():
                return matches, 'old_memberid_but_memberid_exists'

            # Check if a pending user exists. This shouldn't ever happen (a pending user is recently
            # enrolled, and an existing user will have been member for a long time).
            if User.objects.filter(memberid=old_member.memberid, is_pending=True).exists():
                # Give the same error ("user exists, you need to use your new password")
                return matches, 'old_memberid_but_memberid_exists'

            # Verify that they exist in the membersystem (this turned out to be an incorrect assumption)
            if not Actor.get_personal_members().filter(memberid=old_member.memberid).exists():
                # We're not quite sure why this can happen, so we'll just give them the invalid
                # credentials message - but this might be confusing for those who were able to log
                # in previously.
                return matches, 'invalid_credentials'

            # Create the new user
            try:
                # Check if the user's already created as inactive
                user = User.get_users().get(memberid=old_member.memberid, is_inactive=True)
                user.is_inactive = False
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
    # Check that the password is long enough
    if len(request.POST['password']) < settings.USER_PASSWORD_LENGTH:
        return None, 'too_short_password'

    # Check that the email address is valid
    if not validator.email(request.POST['email']):
        return None, 'invalid_email'

    try:
        user = verify_memberid(
            ip_address=request.META['REMOTE_ADDR'],
            memberid=request.POST['memberid'],
            country_code=request.POST['country'],
            zipcode=request.POST['zipcode'],
        )

        if not user.is_inactive:
            return None, 'user_exists'

        user.get_actor().set_email(request.POST['email'].strip())
        user.is_inactive = False
        user.set_password(request.POST['password'])
        user.save()

        authenticate(user=user)
        log_user_in(request, user)

        try:
            t = loader.get_template('common/user/login/registered_email.txt')
            c = RequestContext(request)
            send_mail(EMAIL_REGISTERED_SUBJECT, t.render(c), settings.DEFAULT_FROM_EMAIL, [user.get_email()])
        except (SMTPException, SSLError):
            # Silently log and ignore this error. Consider warning the user that the email wasn't sent?
            logger.warning(u"Klarte ikke å sende registreringskvitteringepost",
                exc_info=sys.exc_info(),
                extra={'request': request}
            )

        return user, None

    except MemberidLookupsExceeded:
        return None, 'memberid_lookups_exceeded'

    except CountryDoesNotExist:
        raise PermissionDenied

    except (NoMatchingMemberid, ActorIsNotPersonalMember, ValueError):
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
    except (SMTPException, SSLError):
        # Silently log and ignore this error. Consider warning the user that the email wasn't sent?
        logger.warning(u"Klarte ikke å sende registreringskvitteringepost",
            exc_info=sys.exc_info(),
            extra={'request': request}
        )

    return user, None
