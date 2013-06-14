# encoding: utf-8
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.core import urlresolvers
from django.utils.log import getLogger
from django.core.urlresolvers import resolve, Resolver404

import re

from core.models import Site
from association.models import Association

logger = getLogger('django.request')

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
        if request.user.is_authenticated() and request.user.has_perm('user.sherpa'):
            m = re.match(r'/sherpa/aktiv-forening/(?P<association>\d+)/', request.path)
            if m is not None:
                # Note: this object will be copied in session for a while and will NOT get updated even if the original object is.
                association = Association.objects.get(id=m.groupdict()['association'])
                if not association in request.user.get_profile().all_associations():
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
            if not request.user.has_perm('user.sherpa'):
                raise PermissionDenied

            # No active association set
            if not 'active_association' in request.session:
                if len(request.user.get_profile().all_associations()) == 1:
                    # The user has only access to 1 association, set it automatically
                    return redirect('/sherpa/aktiv-forening/%s/' % request.user.get_profile().all_associations()[0].id)
                else:
                    # Let the user choose
                    context = {'next': request.get_full_path()}
                    return render(request, 'common/admin/set_active_association.html', context)

            # Accessing CMS-functionality, but no site set
            if request.session['active_association'].site is None and (
                request.path.startswith('/sherpa/cms/') or
                request.path.startswith('/sherpa/nyheter/') or
                request.path.startswith('/sherpa/annonser/') or
                request.path.startswith(u'/sherpa/analyse/søk/')):
                return render(request, 'common/admin/no_association_site.html')

class DeactivatedEnrollment():
    def process_request(self, request):
        from enrollment.models import State
        # The enrollment slug is duplicated and hardcoded here :(
        # However, it's not really likely to change often since it's an important URL.
        if request.path.startswith('/innmelding') and not State.objects.all()[0].active:
            return render(request, 'main/enrollment/unavailable.html')
