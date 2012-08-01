from analytics.models import Visitor, Request, Parameter, Pageview
from django import http
from django.contrib.sites.models import Site
from django.conf import settings
from django.http import HttpResponsePermanentRedirect
from django.core.mail import mail_managers
from django.utils.http import urlquote
from django.core import urlresolvers
from django.utils.log import getLogger

from datetime import datetime
import hashlib
import re

logger = getLogger('django.request')

# Make sure models are loaded. This fixes a TypeError that
# occurs when restarting the gunicorn server.
from django.db.models.loading import cache as model_cache
if not model_cache.loaded:
    model_cache.get_models()

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

class RedirectTrailingDot():
    def process_request(self, request):
        # If hostname contains a trailing dot, strip it with redirect
        # - mainly to support the sites framework.
        # This should preferably be in the nginx config, but it seems to ignore the trailing dot.
        domain = request.get_host().split(':', 1)[0]
        if domain.endswith('.'):
            return HttpResponsePermanentRedirect("http://%s%s" % (domain[:-1], request.get_full_path()))

class Sites():
    def process_request(self, request):
        request.site = Site.objects.get(domain=request.get_host().split(":")[0])

class Analytics():
    def process_request(self, request):
        # Don't process requests to static files
        statics = ['/favicon.ico', '/robots.txt']
        if request.path in statics or request.path.startswith(settings.STATIC_URL):
            return

        # Store new visitor sessions
        if not 'visitor' in request.session:
            if request.user.is_authenticated():
                # Logged-in user without a visitor in session.
                # In theory, this should never happen.
                visitor = request.user.get_profile().visitor
                request.session['visitor'] = visitor.id
            else:
                # Completely new user
                visitor = Visitor()
                visitor.save()
                request.session['visitor'] = visitor.id
        else:
            visitor = Visitor.objects.get(id=request.session['visitor'])

        requestObject = Request(
            visitor=visitor,
            http_method=request.method,
            path=request.path[:2048],
            server_host=request.get_host(),
            client_ip=request.META.get('REMOTE_ADDR', ''),
            client_host=request.META.get('REMOTE_HOST', ''),
            referrer=request.META.get('HTTP_REFERER', '')[:2048],
            enter=datetime.now(),
            ajax=request.is_ajax())
        requestObject.save()

        for key, value in request.GET.items():
            p = Parameter(request=requestObject, key=key, value=value)
            p.save()

        request.session['request'] = requestObject

    def process_response(self, request, response):
        if 'request' in request.session:
            del request.session['request']
        return response

class CommonMiddlewareMonkeypatched(object):
    """
    This is a monkeypatch of Djangos CommonMiddleware.

    Its purpose is to decode the query string with the encoding specified in settings,
    instead of ascii.

    ".decode(settings.DEFAULT_CHARSET)" has been appended to the second last line in
    process_request.

    At the time of this writing, we're running on Django 1.4.
    When updating, REMEMBER TO UPDATE THIS MONKEYPATCH ACCORDINGLY!
    """

    def process_request(self, request):
        """
        Check for denied User-Agents and rewrite the URL based on
        settings.APPEND_SLASH and settings.PREPEND_WWW
        """

        # Check for denied User-Agents
        if 'HTTP_USER_AGENT' in request.META:
            for user_agent_regex in settings.DISALLOWED_USER_AGENTS:
                if user_agent_regex.search(request.META['HTTP_USER_AGENT']):
                    logger.warning('Forbidden (User agent): %s', request.path,
                        extra={
                            'status_code': 403,
                            'request': request
                        }
                    )
                    return http.HttpResponseForbidden('<h1>Forbidden</h1>')

        # Check for a redirect based on settings.APPEND_SLASH
        # and settings.PREPEND_WWW
        host = request.get_host()
        old_url = [host, request.path]
        new_url = old_url[:]

        if (settings.PREPEND_WWW and old_url[0] and
                not old_url[0].startswith('www.')):
            new_url[0] = 'www.' + old_url[0]

        # Append a slash if APPEND_SLASH is set and the URL doesn't have a
        # trailing slash and there is no pattern for the current path
        if settings.APPEND_SLASH and (not old_url[1].endswith('/')):
            urlconf = getattr(request, 'urlconf', None)
            if (not urlresolvers.is_valid_path(request.path_info, urlconf) and
                    urlresolvers.is_valid_path("%s/" % request.path_info, urlconf)):
                new_url[1] = new_url[1] + '/'
                if settings.DEBUG and request.method == 'POST':
                    raise RuntimeError((""
                    "You called this URL via POST, but the URL doesn't end "
                    "in a slash and you have APPEND_SLASH set. Django can't "
                    "redirect to the slash URL while maintaining POST data. "
                    "Change your form to point to %s%s (note the trailing "
                    "slash), or set APPEND_SLASH=False in your Django "
                    "settings.") % (new_url[0], new_url[1]))

        if new_url == old_url:
            # No redirects required.
            return
        if new_url[0]:
            newurl = "%s://%s%s" % (
                request.is_secure() and 'https' or 'http',
                new_url[0], urlquote(new_url[1]))
        else:
            newurl = urlquote(new_url[1])
        if request.META.get('QUERY_STRING', ''):
            newurl += '?' + request.META['QUERY_STRING'].decode(settings.DEFAULT_CHARSET)
        return http.HttpResponsePermanentRedirect(newurl)

    def process_response(self, request, response):
        "Send broken link emails and calculate the Etag, if needed."
        if response.status_code == 404:
            if settings.SEND_BROKEN_LINK_EMAILS and not settings.DEBUG:
                # If the referrer was from an internal link or a non-search-engine site,
                # send a note to the managers.
                domain = request.get_host()
                referer = request.META.get('HTTP_REFERER', None)
                is_internal = _is_internal_request(domain, referer)
                path = request.get_full_path()
                if referer and not _is_ignorable_404(path) and (is_internal or '?' not in referer):
                    ua = request.META.get('HTTP_USER_AGENT', '<none>')
                    ip = request.META.get('REMOTE_ADDR', '<none>')
                    mail_managers("Broken %slink on %s" % ((is_internal and 'INTERNAL ' or ''), domain),
                        "Referrer: %s\nRequested URL: %s\nUser agent: %s\nIP address: %s\n" \
                                  % (referer, request.get_full_path(), ua, ip),
                                  fail_silently=True)
                return response

        # Use ETags, if requested.
        if settings.USE_ETAGS:
            if response.has_header('ETag'):
                etag = response['ETag']
            else:
                etag = '"%s"' % hashlib.md5(response.content).hexdigest()
            if response.status_code >= 200 and response.status_code < 300 and request.META.get('HTTP_IF_NONE_MATCH') == etag:
                cookies = response.cookies
                response = http.HttpResponseNotModified()
                response.cookies = cookies
            else:
                response['ETag'] = etag

        return response

def _is_ignorable_404(uri):
    """
    Returns True if a 404 at the given URL *shouldn't* notify the site managers.
    """
    if getattr(settings, 'IGNORABLE_404_STARTS', ()):
        import warnings
        warnings.warn('The IGNORABLE_404_STARTS setting has been deprecated '
                      'in favor of IGNORABLE_404_URLS.',
                      PendingDeprecationWarning)
        for start in settings.IGNORABLE_404_STARTS:
            if uri.startswith(start):
                return True
    if getattr(settings, 'IGNORABLE_404_ENDS', ()):
        import warnings
        warnings.warn('The IGNORABLE_404_ENDS setting has been deprecated '
                      'in favor of IGNORABLE_404_URLS.',
                      PendingDeprecationWarning)
        for end in settings.IGNORABLE_404_ENDS:
            if uri.endswith(end):
                return True
    return any(pattern.search(uri) for pattern in settings.IGNORABLE_404_URLS)

def _is_internal_request(domain, referer):
    """
    Returns true if the referring URL is the same domain as the current request.
    """
    # Different subdomains are treated as different domains.
    return referer is not None and re.match("^https?://%s/" % re.escape(domain), referer)