from functools import wraps
from django.utils.decorators import available_attrs
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages

def user_requires(test_func, redirect_to='user.login.views.login', message=None):
    """
    Decorator that is very similar to Djangos 'user_passes_test', but differs
    in that it simply redirects the user to the given view and doesn't require
    it to be a login view.
    """

    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            else:
                if message is not None:
                    messages.info(request, message)
                return HttpResponseRedirect(reverse(redirect_to))
        return _wrapped_view
    return decorator
