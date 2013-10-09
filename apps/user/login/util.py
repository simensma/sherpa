# encoding: utf-8
from django.contrib.auth import authenticate, login as log_user_in

from user.models import User
from user.util import authenticate_sherpa2_user, authenticate_users
from focus.models import Actor
from sherpa25.models import import_fjelltreffen_annonser

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
