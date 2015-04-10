# encoding: utf-8
from django.conf.urls import patterns, include, url

handler403 = 'page.views.permission_denied'
handler404 = 'page.views.page_not_found'
handler500 = 'page.views.server_error'

urlpatterns = patterns('',
    url(r'^', include('sherpa.urls_common_pre')),

    url(r'^', include('core.urls')),
    url(r'^', include('montis.urls')),
    url(r'^foreninger/', include('foreninger.urls')),

    # Note: This slug-prefix is duplicated in the DeactivatedEnrollment middleware
    url(r'^innmelding/', include('enrollment.urls')),
    url(r'^gavemedlemskap/', include('enrollment.gift.urls')),

    url(r'^medlem/', include('membership.urls')),
    url(r'^medlemsservice/', 'membership.views.service'),
    url(r'^instagram/', include('instagram.urls')),
    url(r'^fjelltreffen/', include('fjelltreffen.urls')),
    url(r'^foremeldinger/', include('conditions.urls')),
    url(r'^fotokonkurranse/', include('fotokonkurranse.urls')),

    url(r'^connect/', include('connect.urls')),
    url(r'^api/', include('api.urls')),
    url(r'^payment/(?P<slug>.*)', 'page.views.perform_site_redirect', kwargs={'url': 'payment/'}),

    # Note that this URL (more specifically, o/applications/) is duplicated and hardcoded in the
    # CheckOauth2ApplicationsPermission middleware
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),

    url(r'^', include('sherpa.urls_redirects_central')),
    url(r'^', include('sherpa.urls_redirects_common')),
    url(r'^', include('sherpa.urls_common_post')),
)
