# encoding: utf-8
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.core import urlresolvers
from django.core.urlresolvers import resolve, Resolver404
from django.contrib.auth import logout

from datetime import datetime
import re
import logging
import sys

from core.models import Site
from association.models import Association
from focus.models import Actor

logger = logging.getLogger('sherpa')

# Make sure models are loaded. This fixes a TypeError that
# occurs when restarting the gunicorn server.
from django.db.models.loading import cache as model_cache
if not model_cache.loaded:
    model_cache.get_models()

from django import template
template.add_to_builtins('core.templatetags.url')

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

class SetActiveAssociation(object):
    def process_request(self, request):
        # This "view" is very special, needs to avoid certain middleware logic that depends on 'active_association'.
        if request.user.is_authenticated() and request.user.has_perm('sherpa'):
            m = re.match(r'/sherpa/aktiv-forening/(?P<association>\d+)/', request.path)
            if m is not None:
                # Note: this object will be copied in session for a while and will NOT get updated even if the original object is.
                association = Association.objects.get(id=m.groupdict()['association'])
                if not association in request.user.all_associations():
                    raise PermissionDenied

                request.session['active_association'] = association
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

            # No active association set
            if not 'active_association' in request.session:
                if len(request.user.all_associations()) == 1:
                    # The user has only access to 1 association, set it automatically
                    return redirect('/sherpa/aktiv-forening/%s/' % request.user.all_associations()[0].id)
                else:
                    # Let the user choose
                    context = {'next': request.get_full_path()}
                    return render(request, 'common/admin/set_active_association.html', context)

            # Accessing CMS-functionality, but no site set
            if request.session['active_association'].site is None:
                site_required_paths = [
                    u'/sherpa/cms/',
                    u'/sherpa/nyheter/',
                    u'/sherpa/annonser/',
                    u'/sherpa/analyse/søk/'
                ]
                for path in site_required_paths:
                    if request.path.startswith(path):
                        return render(request, 'common/admin/no_association_site.html')

class DeactivatedEnrollment():
    def process_request(self, request):
        from enrollment.models import State
        # The enrollment slug is duplicated and hardcoded here :(
        # However, it's not really likely to change often since it's an important URL.
        if request.path.startswith('/innmelding') and not State.objects.all()[0].active:
            return render(request, 'main/enrollment/unavailable.html')

class FocusDowntime():
    def process_request(self, request):
        now = datetime.now()
        focus_is_down = False
        for downtime in settings.FOCUS_DOWNTIME_PERIODS:
            if now >= downtime['from'] and now < downtime['to']:
                focus_is_down = True

        if focus_is_down:
            # All these paths are hardcoded! :(
            # These are the paths that can be directly accessed and require Focus to function
            focus_required_paths = [
                ('/innmelding', 'main/enrollment/unavailable.html'),
                ('/minside', 'common/user/unavailable.html'),
                ('/fjelltreffen', 'main/fjelltreffen/unavailable.html'),
            ]
            for path, template in focus_required_paths:
                if request.path.startswith(path):
                    return render(request, template)

class ActorDoesNotExist():
    def process_request(self, request):
        if request.user.is_authenticated() and request.user.is_member():
            try:
                # This call performs the lookup in Focus (or uses the cache if applicable, which is fine)
                request.user.get_actor()
            except Actor.DoesNotExist:
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
