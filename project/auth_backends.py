from django.contrib.auth.models import User, check_password

class EmailBackend(object):

    supports_inactive_user = False

    def authenticate(self, username=None, password=None):
        # Check username first (instead of e.g. assuming email for a <name>@<domain>.<tld> regex)
        # because, who knows, maybe someone stored their username with the @ and . characters.
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                return user
            else:
                return None
        except User.DoesNotExist:
            # Try username as email instead
            pass

        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
            else:
                return None
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
