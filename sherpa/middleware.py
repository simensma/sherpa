# encoding: utf-8
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.core import urlresolvers
from django.core.urlresolvers import resolve, Resolver404
from django.contrib.auth import logout
from django.utils import translation

import re
import logging
import sys

from core.models import Site
from core.util import focus_is_down
from foreninger.models import Forening
from focus.models import Actor, Enrollment
from enrollment.util import current_template_layout

logger = logging.getLogger('sherpa')

# Make sure models are loaded. This fixes a TypeError that
# occurs when restarting the gunicorn server.
from django.db.models.loading import cache as model_cache
if not model_cache.loaded:
    model_cache.get_models()

from django import template
template.add_to_builtins('core.templatetags.url')

class DefaultLanguage():
    def process_request(self, request):
        # DNT Connect supports language selection now, so do nothing if dnt connect is in session.
        # Note that it's *possible* someone initiated DNT connect without fulfilling it, which would
        # let them view other pages with mixed translation results.
        if 'dntconnect' in request.session:
            return

        # English enrollment form is activated through a unique URL which sets this session var.
        # Note that this will also translate other unrelated pages (like user page registration).
        if 'activated_english_enrollment' in request.session:
            if request.LANGUAGE_CODE != 'en':
                translation.activate('en')
            return

        # Force norwegian for all requests.
        if request.LANGUAGE_CODE != settings.LANGUAGE_CODE:
            translation.activate(settings.LANGUAGE_CODE)

class Sites():
    def process_request(self, request):
        try:
            request.site = Site.objects.get(domain=request.get_host().lower().split(":")[0])
            request.urlconf = "sherpa.urls_%s" % request.site.template.name
            urlresolvers.set_urlconf(request.urlconf)
        except Site.DoesNotExist:
            # Todo: This should be more than a regular 404, as it's a completely unknown _site_.
            raise Http404

class CurrentApp(object):
    def process_request(self, request):
        try:
            request.current_app = resolve(request.path).app_name
        except Resolver404:
            request.current_app = ''

class DecodeQueryString(object):
    def process_request(self, request):
        # Some browsers (guess which), and also the Bing bot, don't follow the spec, and send
        # non-ascii query string characters, without using percent-encoding.
        # Guess the encoding, trying ascii first, and re-encode with default charset
        for encoding in ['ascii', 'utf-8', 'iso-8859-1', 'windows-1252']:
            try:
                request.META['QUERY_STRING'] = request.META['QUERY_STRING'].decode(encoding).encode(settings.DEFAULT_CHARSET)
                return
            except UnicodeDecodeError:
                pass
        # Unable to decode the query string. Just leave it as it is, and if any later usage
        # of it leads to a decoding error, let it happen and be logged for further inspection.

class SetActiveForening(object):
    def process_request(self, request):
        # This "view" is very special, needs to avoid certain middleware logic that depends on 'active_forening'.
        if request.user.is_authenticated() and request.user.has_perm('sherpa'):
            m = re.match(r'/sherpa/aktiv-forening/(?P<forening>\d+)/', request.path)
            if m is not None:
                # Note: this object will be copied in session for a while and will NOT get updated even if the original object is.
                forening = Forening.objects.get(id=m.groupdict()['forening'])
                if not forening in request.user.all_foreninger():
                    raise PermissionDenied

                request.session['active_forening'] = forening
                if request.GET.get('next', '') != '':
                    return redirect(request.GET['next'])
                else:
                    return redirect('admin.views.index')

class CheckSherpaPermissions(object):
    def process_request(self, request):
        if request.current_app == 'admin':
            # Not logged in
            if not request.user.is_authenticated():
                return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

            # Missing sherpa-permission
            if not request.user.has_perm('sherpa'):
                raise PermissionDenied

            # No active forening set
            if not 'active_forening' in request.session:
                if len(request.user.all_foreninger()) == 1:
                    # The user has only access to 1 forening, set it automatically
                    return redirect('/sherpa/aktiv-forening/%s/' % request.user.all_foreninger()[0].id)
                else:
                    # Let the user choose
                    context = {'next': request.get_full_path()}
                    return render(request, 'common/admin/set_active_forening.html', context)

            # Accessing CMS-functionality, but no site set
            if request.session['active_forening'].site is None:
                site_required_paths = [
                    u'/sherpa/cms/',
                    u'/sherpa/nyheter/',
                    u'/sherpa/annonser/',
                    u'/sherpa/analyse/'
                ]
                for path in site_required_paths:
                    if request.path.startswith(path):
                        return render(request, 'common/admin/no_forening_site.html')

class DeactivatedEnrollment():
    def process_request(self, request):
        from enrollment.models import State
        state = State.objects.all()[0]

        # The enrollment slug is duplicated and hardcoded here :(
        # However, it's not really likely to change often since it's an important URL.
        if request.path.startswith('/innmelding') and not state.active:
            context = current_template_layout(request)
            return render(request, 'main/enrollment/unavailable.html', context)

        # Another issue: If passing through DNT Connect, and card payment is deactivated,
        # there is no means for payment available. Inform them immediately
        if request.path.startswith('/innmelding') and 'dntconnect' in request.session and not state.card:
            return render(request, 'main/connect/signon_enrollment_card_deactivated.html')

class FocusDowntime():
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Use process_view instead of process_request here because some rendered pages need the csrf token,
        which is generated on process_view by the csrf middleware.
        """
        if focus_is_down():
            # All these paths are hardcoded! :(
            # These are the paths that can be directly accessed and require Focus to function
            focus_required_paths = [
                ('/innmelding', 'main/enrollment/unavailable.html'),
                ('/minside', 'common/user/unavailable.html'),
                ('/fjelltreffen', 'main/fjelltreffen/unavailable.html'),
                ('/connect/signon/login', 'main/connect/signon_unavailable.html'),
                ('/connect/signon/velg-bruker', 'main/connect/signon_unavailable.html'),
                ('/connect/signon/registrer', 'main/connect/signon_unavailable.html'),
            ]
            for path, template in focus_required_paths:
                if request.path.startswith(path):
                    # Extra context update for enrollment URLs
                    context = {}
                    if request.path.startswith('/innmelding'):
                        context.update(current_template_layout(request))
                    return render(request, template, context)

class ActorDoesNotExist():
    def process_request(self, request):
        # Skip this check if Focus is currently down
        if not focus_is_down() and request.user.is_authenticated() and request.user.is_member():
            try:
                # This call performs the lookup in Focus (or uses the cache if applicable, which is fine)
                request.user.get_actor()
            except Actor.DoesNotExist as e:
                if request.user.is_pending:
                    # The user is pending - no idea why Actor.DoesNotExist is raised, just re-raise it
                    raise e

                logger.warning(u"Pålogget bruker mangler tilsvarende medlemsnummer i Actor",
                    exc_info=sys.exc_info(),
                    extra={
                        'request': request,
                        'memberid': request.user.memberid
                    }
                )
                request.user.is_expired = True
                request.user.save()
                logout(request)
                return render(request, 'common/user/memberid_does_not_exist.html')
            except Enrollment.DoesNotExist as e:
                if not request.user.is_pending:
                    # The user isn't pending - no idea why Enrollment.DoesNotExist is raised, just re-raise it
                    raise e

                if not request.user.verify_still_pending(ignore_cache=True):
                    # Ah, they *just* got an Actor. That's fine, but redirect to the home page since they could
                    # be headed to some view that requires a pending user.
                    return redirect('user.views.home')

                logger.warning(u"Pålogget pending-bruker mangler tilsvarende medlemsnummer i Enrollment",
                    exc_info=sys.exc_info(),
                    extra={
                        'request': request,
                        'memberid': request.user.memberid
                    }
                )
                request.user.is_expired = True
                request.user.save()
                logout(request)
                return render(request, 'common/user/memberid_does_not_exist.html')
