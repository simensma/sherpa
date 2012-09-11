# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

handler404 = 'page.views.page_not_found'
handler500 = 'page.views.server_error'

urlpatterns = patterns('',
    url(r'^', include('sherpa.urls_common_pre')),

    url(r'^', include('core.urls')),
    url(r'^foreninger/', include('association.urls')),

    # Note: This slug-prefix is duplicated in the DeactivatedEnrollment middleware
    url(r'^innmelding/', include('enrollment.urls')),
    url(r'^gavemedlemskap/', include('enrollment.urls_gift')),

    url(r'^medlem/', include('membership.urls')),
    url(r'^medlemsservice/', 'membership.views.service'),
    url(r'^instagram/', include('instagram.urls')),

    url(r'^', include('sherpa.urls_redirects')),
    url(r'^', include('sherpa.urls_common_post')),
)
