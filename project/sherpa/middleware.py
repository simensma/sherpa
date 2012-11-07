from django import http
from django.shortcuts import render
from django.conf import settings
from django.http import Http404, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.core.mail import mail_managers
from django.core.exceptions import PermissionDenied
from django.utils.http import urlquote
from django.core import urlresolvers
from django.utils.log import getLogger
from django.core.urlresolvers import resolve, Resolver404
from django.contrib import messages
from django.core.urlresolvers import reverse

from datetime import datetime
import hashlib
import re

from core.models import Site, SiteTemplate
from association.models import Association

logger = getLogger('django.request')

# Make sure models are loaded. This fixes a TypeError that
# occurs when restarting the gunicorn server.
from django.db.models.loading import cache as model_cache
if not model_cache.loaded:
    model_cache.get_models()

from django import template
template.add_to_builtins('core.templatetags.url')

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
        try:
            request.site = Site.objects.get(domain=request.get_host().split(":")[0])
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


class SetActiveAssociation(object):
    def process_request(self, request):
        # This "view" is very special, needs to avoid certain middleware logic that depends on 'active_association'.
        if request.user.is_authenticated() and request.user.has_perm('user.sherpa'):
            m = re.match(r'/sherpa/aktiv-forening/(?P<association>\d+)/', request.path)
            if m != None:
                # Note: this object will be copied in session for a while and will NOT get updated even if the original object is.
                association = Association.objects.get(id=m.groupdict()['association'])
                if not association in request.user.get_profile().associations.all():
                    raise PermissionDenied

                request.session['active_association'] = association
                if request.META.get('HTTP_REFERER') != None:
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                else:
                    return HttpResponseRedirect(reverse('admin.views.index'))


class CheckSherpaPermissions(object):
    def process_request(self, request):
        if request.current_app == 'admin':
            # Not logged in
            if not request.user.is_authenticated():
                return HttpResponseRedirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

            # Missing sherpa-permission
            if not request.user.has_perm('user.sherpa'):
                raise PermissionDenied

            # No active association set
            if not 'active_association' in request.session:
                return render(request, 'main/admin/set_active_association.html')

            # Accessing CMS-functionality, but no site set
            if request.session['active_association'].site == None and (
                request.path.startswith('/sherpa/cms/') or
                request.path.startswith('/sherpa/nyheter/') or
                request.path.startswith('/sherpa/annonser/')):
                messages.add_message(request, messages.ERROR, 'no_association_site')
                return HttpResponseRedirect(reverse('admin.views.index'))

class DeactivatedEnrollment():
    def process_request(self, request):
        from enrollment.models import State
        # The enrollment slug is duplicated and hardcoded here :(
        # However, it's not really likely to change often since it's an important URL.
        if request.path.startswith('/innmelding') and not State.objects.all()[0].active:
            return render(request, 'main/enrollment/unavailable.html')
