# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

handler404 = 'page.views.page_not_found'
handler500 = 'page.views.server_error'

urlpatterns = patterns('',
    # Sherpa admin interface
    url(r'^sherpa/', include('admin.urls')),

    # Articles
    url(r'^artikler/', include('articles.urls')),

    # User authentication
    url(r'^minside/', include('user.urls')),
    url(r'^foreninger/', include('association.urls')),

    # Enrollment
    url(r'^innmelding/', include('enrollment.urls')),

    # Membership
    url(r'^medlem/', include('membership.urls')),
    url(r'^medlemsservice/', 'membership.views.service'),

    # Search
    url(ur'^søk/', 'page.views.search'),

    # Ads
    url(r'^annonse/(?P<ad>\d+)/$', 'page.views.ad'),

    # Redirect known paths to the old site
    url(r'^', include('sherpa.url_redirects')),

    # Not a known view, treat it as a page
    url(r'^$', 'page.views.page', kwargs={'slug': ""}),
    url(r'^(?P<slug>.+)/$', 'page.views.page'),
)
