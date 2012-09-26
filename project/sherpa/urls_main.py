# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

handler404 = 'page.views.page_not_found'
handler500 = 'page.views.server_error'

urlpatterns = patterns('',
    # Core urls
    url(r'^', include('core.urls')),

    # Sherpa admin interface
    url(r'^sherpa/', include('admin.urls')),

    # Articles
    url(r'^nyheter/', include('articles.urls')),

    # User authentication
    url(r'^minside/', include('user.urls')),
    url(r'^foreninger/', include('association.urls')),

    # Enrollment
    # Note: This slug-prefix is duplicated in the DeactivatedEnrollment middleware
    url(r'^innmelding/', include('enrollment.urls')),

    # Membership
    url(r'^medlem/', include('membership.urls')),
    url(r'^medlemsservice/', 'membership.views.service'),

    # Search
    url(ur'^søk/', 'page.views.search'),

    # Ads
    url(r'^annonse/(?P<ad>\d+)/$', 'page.views.ad'),

    # All kinds of redirects
    url(r'^', include('sherpa.urls_redirects')),

    # Not a known view, treat it as a page
    url(r'^$', 'page.views.page', kwargs={'slug': ""}),
    url(r'^(?P<slug>.+)/$', 'page.views.page'),
)
