# encoding: utf-8
import re
import logging
import sys

from django.shortcuts import render, redirect
from django.conf import settings
from django.core import urlresolvers
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import resolve, Resolver404
from django.contrib.auth import logout
from django.utils import translation
from django.db import connections

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

class DBConnection():
    """Checks connections to external DBs and saves the state in the request object"""
    def process_request(self, request):
        external_databases = ['focus', 'sherpa-2', 'sherpa-25']

        # Cache the connection status for a few minutes. It's okay to display the 500 page for a few request
        # if there's a short-lasting problem. It's when a DB goes unavailable for a long while that we want
        # to give a nicer error message.
        request.db_connections = cache.get('db_connection_status')
        if request.db_connections is None:
            request.db_connections = {}
            for database in external_databases:
                try:
                    connections[database].cursor() # Will select server version from the DB
                    request.db_connections[database] = {'available': True}
                except Exception:
                    request.db_connections[database] = {'available': False}
            cache.set('db_connection_status', request.db_connections, 60 * 15)

class DefaultLanguage():
    def process_request(self, request):
        # DNT Connect (only for DNT Oslo/the 'columbus' client) supports language selection now, so do
        # nothing if dnt connect is in session. Note that it's *possible* someone initiated DNT connect
        # without fulfilling it, which would let them view other pages with mixed translation results.
        if 'dntconnect' in request.session and request.session['dntconnect']['client_id'] == 'columbus':
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
            request.urlconf = "sherpa.urls_%s" % request.site.template
            urlresolvers.set_urlconf(request.urlconf)
        except Site.DoesNotExist:
            # Unknown host name, redirect to the main site.
            # Rendering 404 in the main site's layout would probably also make sense, but don't do that for now since
            # all links will be relative and hence keep the incorrect host name.
            main_site = Site.objects.get(id=1)
            return redirect('http://%s/' % main_site.domain)

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

class ChangeActiveForening(object):
    def process_request(self, request):
        # This lets the user change the active forening. It could be a view, but it needs to apply before the
        # ActiveForening middleware logic.
        if request.user.is_authenticated() and request.user.has_perm('sherpa'):
            m = re.match(r'/sherpa/aktiv-forening/(?P<forening>\d+)/', request.path)
            if m is not None:
                forening = Forening.objects.get(id=m.groupdict()['forening'])
                if not forening in request.user.all_foreninger():
                    raise PermissionDenied

                request.session['active_forening'] = forening.id
                if request.GET.get('next', '') != '':
                    return redirect(request.GET['next'])
                else:
                    return redirect('admin.views.index')

class ActiveForening(object):
    """The session contains an 'active_forening' id of the currently active forening. Get the object from DB each
    request based on the ID in session. We used to save the entire forening object for efficiency, but that gives
    us small problems with cache invalidation, and large problems when deploying database migrations that change
    these objects."""
    def process_request(self, request):
        if 'active_forening' in request.session:
            # First; handle existing sessions which used to save the actual object
            # You may remove this check at some point (when all sessions have converted their value or timed out)
            if not type(request.session['active_forening']) == int:
                request.session['active_forening'] = request.session['active_forening'].id

            try:
                request.active_forening = Forening.objects.get(id=request.session['active_forening'])
            except Forening.DoesNotExist:
                # It might have been removed, remove it and let the user choose a new one
                del request.session['active_forening']

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
            if not hasattr(request, 'active_forening'):
                if len(request.user.all_foreninger()) == 1:
                    # The user has only access to 1 forening, set it automatically
                    return redirect('/sherpa/aktiv-forening/%s/' % request.user.all_foreninger()[0].id)
                else:
                    # Let the user choose
                    context = {'next': request.get_full_path()}
                    return render(request, 'common/admin/set_active_forening.html', context)

    def process_view(self, request, view_func, *args, **kwargs):
        if request.current_app == 'admin' and request.path.startswith(u'/sherpa/nettsteder'):
            # Accessing 'sites' subapp in admin
            try:
                site = [Site.objects.get(id=arg['site']) for arg in args if type(arg) == dict and 'site' in arg]
                if len(site) == 1:
                    site = site[0]

                    # Verify that the user has access to this site (transitive by forening)
                    if not site.forening in request.user.all_foreninger():
                        raise PermissionDenied

            except Site.DoesNotExist:
                # The specified site doesn't exist
                return redirect('admin.views.setup_site')

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
