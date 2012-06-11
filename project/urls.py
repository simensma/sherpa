# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

handler404 = 'page.views.page_not_found'
handler500 = 'page.views.server_error'

urlpatterns = patterns('',
    # Sherpa admin interface
    url(r'^sherpa/', include('admin.urls')),
    url(r'^admin/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': '/sherpa/'}),

    # Articles
    url(r'^artikler/', include('articles.urls')),

    # User authentication
    url(r'^', include('user.urls')),
    url(r'^foreninger/', include('group.urls')),

    # Enrollment
    url(r'^innmelding/', include('enrollment.urls')),

    # Membership
    url(r'^medlem/', include('membership.urls')),
    url(r'^medlemsservice/', 'membership.views.service'),

    # Search
    url(ur'^søk/', 'page.views.search'),

    # Redirect known paths to the old site
    url(r'^images/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': "http://www.turistforeningen.no/images/"}),
    url(r'^album/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': "http://www.turistforeningen.no/album/"}),

    # Not a known view, treat it as a page
    url(r'^$', 'page.views.page', kwargs={'slug': ""}),
    url(r'^(?P<slug>.+)/$', 'page.views.page'),
)
