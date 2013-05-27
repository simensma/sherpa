from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend

class CustomBackend(ModelBackend):
    supports_inactive_user = False

    # Just return the user - the authentication logic is done in a utility method instead.
    # For the reason, see the comments on 'authenticate_users' in apps/user/util.py
    def authenticate(self, user=None):
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None