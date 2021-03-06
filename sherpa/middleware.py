# encoding: utf-8
from datetime import datetime
import re
import logging
import sys
import multiprocessing

from django.shortcuts import render, redirect
from django.conf import settings
from django.core import urlresolvers
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import resolve, Resolver404
from django.contrib.auth import logout
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import translation
from django.db import connections

import pyodbc

from core.models import Site
from foreninger.models import Forening
from focus.models import Actor, Enrollment
from enrollment.util import current_template_layout

logger = logging.getLogger('sherpa')

from django import template
template.add_to_builtins('core.templatetags.url')

class TemporaryCorsMiddleware():
    """Temporary middleware - until we've verified that the DNT app will send an 'Origin' header so that we can use
    the corsheaders app solely for handling CORS requests, this app will handle it manually"""
    def process_request(self, request):
        if request.path.startswith('/api/') or \
            request.path.startswith('/ekstern-betaling/') or \
            request.path.startswith('/o/token/'):
            if request.method == 'OPTIONS':
                # Handle CORS preflight
                request_headers = request.META.get('HTTP_ACCESS_CONTROL_REQUEST_HEADERS')
                response = HttpResponse()
                if request_headers is not None:
                    response['Access-Control-Allow-Headers'] = request_headers
                response['Access-Control-Allow-Method'] = 'POST'
                return response

    def process_response(self, request, response):
        if request.path.startswith('/api/') or \
            request.path.startswith('/ekstern-betaling/') or \
            request.path.startswith('/o/token/'):
            response['Access-Control-Allow-Origin'] = '*'
        return response

class Redirect():
    """Domain-specific redirects"""
    def process_request(self, request):
        # At the start of 2015, the main site changed domain from turistforeningen.no to dnt.no. This temporary
        # redirect should be kept for a long while, perhaps about a year.
        requested_host = request.get_host().lower()
        if requested_host.endswith('turistforeningen.no'):
            # Keep the requested subdomain. The turistforeningen.no domain (without subdomain) shouldn't in theory end
            # up here, but handle it just in case.
            if requested_host == 'turistforeningen.no':
                subdomain = 'www'
            else:
                subdomain = requested_host[:-len('.turistforeningen.no')]

            response = HttpResponseRedirect('https://%s.dnt.no%s' % (subdomain, request.get_full_path()))

            # Add CORS header to the redirect response for API requests
            if request.path.startswith('/api/'):
                response['Access-Control-Allow-Origin'] = '*'

            return response

class DBConnection():
    """Checks connections to external DBs and saves the state in the request object"""
    def process_request(self, request):
        # Define the external databases that we want to check here.
        # Note that checks for sherpa-2 and sherpa-25 DBs would NOT work at the moment. This is because the
        # postgis engine needs to check the DB version in its init, and if the connection is down it will
        # raise an exception. We cannot hook into or handle that exception. This is also why the entire site
        # will go down if one of these databases is unavailable.
        # Here's an example stacktrace: http://pastie.org/private/ge6yxjymjfyb6nwtj9ug
        external_databases = ['focus']

        # Cache the connection status for a few minutes. It's okay to display the 500 page for a few request
        # if there's a short-lasting problem. It's when a DB goes unavailable for a long while that we want
        # to give a nicer error message.
        request.db_connections = cache.get('db_connection_status')
        if request.db_connections is None:
            request.db_connections = {}
            for database in external_databases:

                # Perform the connection attempt in a separate process in order to be able to handle timeouts
                def attempt_database_connection():
                    # If the connection fails, the call will throw an exception resulting in a non-zero exit code
                    connections[database].cursor() # Will select server version from the DB

                connection_process = multiprocessing.Process(target=attempt_database_connection)
                connection_process.start()
                connection_process.join(settings.DATABASE_CONNECTION_TIMEOUT)

                # If the connection attempt didn't finish, terminate it; it will get a non-zero exit code
                if connection_process.is_alive():
                    connection_process.terminate()
                    connection_process.join()

                if connection_process.exitcode == 0:
                    request.db_connections[database] = {'is_available': True}
                else:
                    request.db_connections[database] = {
                        'is_available': False,
                        'period_message': "en kort periode", # LIES!
                    }
            cache.set('db_connection_status', request.db_connections, 60)

        # Always assume sherpa-2 and sherpa-25 are available (see comments above).
        request.db_connections['sherpa-2'] = {'is_available': True}
        request.db_connections['sherpa-25'] = {'is_available': True}

        # Override the focus DB's value if we're in a planned downtime period
        # Note that we don't need to cache this; and shouldn't since it's dependent on the current time
        now = datetime.now()
        for downtime in settings.FOCUS_DOWNTIME_PERIODS:
            if now >= downtime['from'] and now < downtime['to']:
                request.db_connections['focus'] = {
                    'is_available': False,
                    'period_message': downtime['period_message'],
                }

    def process_exception(self, request, exception):
        """Handle pyodbc exceptions in case Focus is down (which happens often), so that we don't have to wait for
        the cache to expire. Note that this will only handle exceptions occuring views - not in middleware, which
        currently will happen for logged-in users. Hence, this cache invalidation is not fail-safe (works only if
        a not-logged in user trigges the exception), but at least it should help."""
        if isinstance(exception, pyodbc.Error):
            # Well, we're seeing a pyodbc Error - we could check its arguments for the error code 08S01 which means
            # unavailable, but that's probably not important - just assume that Focus is down, and delete the cache
            # so that the DBConnection middleware can detect it and update its state
            cache.delete('db_connection_status')

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

class CheckOauth2ApplicationsPermission(object):
    """The django-oauth-toolkit requires only a logged-in user. Here we'll append our own rule which is that only
    sherpa-admins have access to managing OAuth2 applications."""
    def process_request(self, request):
        if request.path.startswith(u'/o/applications') and \
            request.user.is_authenticated() and \
            not request.user.has_perm('sherpa_admin'):
            raise PermissionDenied()

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
                return redirect('admin.sites.views.create')

class DeactivatedEnrollment():
    def process_request(self, request):
        from enrollment.models import State
        state = State.objects.all()[0]

        # The enrollment slug is duplicated and hardcoded here :(
        # However, it's not really likely to change often since it's an important URL.
        if request.path.startswith('/innmelding') and not state.active:
            context = current_template_layout(request)
            return render(request, 'central/enrollment/unavailable.html', context)

        # Another issue: If passing through DNT Connect, and card payment is deactivated,
        # there is no means for payment available. Inform them immediately
        if request.path.startswith('/innmelding') and 'dntconnect' in request.session and not state.card:
            return render(request, 'central/connect/signon_enrollment_card_deactivated.html')

class FocusDowntime():
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Use process_view instead of process_request here because some rendered pages need the csrf token,
        which is generated on process_view by the csrf middleware.
        """
        if not request.db_connections['focus']['is_available']:
            # All these paths are hardcoded! :(
            # These are the paths that can be directly accessed and require Focus to function
            focus_required_paths = [
                ('/innmelding', 'central/enrollment/unavailable.html'),
                ('/minside', 'common/user/unavailable.html'),
                ('/fjelltreffen', 'central/fjelltreffen/unavailable.html'),
                ('/connect/signon/login', 'central/connect/signon_unavailable.html'),
                ('/connect/signon/velg-bruker', 'central/connect/signon_unavailable.html'),
                ('/connect/signon/registrer', 'central/connect/signon_unavailable.html'),
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
        if request.db_connections['focus']['is_available'] and request.user.is_authenticated() and request.user.is_member():
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
