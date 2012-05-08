from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    # Sherpa admin interface
    url(r'^sherpa/', include('admin.urls')),
    url(r'^admin/(?P<url>.*)', 'page.views.redirect', kwargs={'prefix': '/sherpa/'}),

    # Articles
    url(r'^artikler/', include('articles.urls')),

    # User authentication
    url(r'^bruker/', include('user.urls')),

    # Enrollment
    url(r'^innmelding/', include('enrollment.urls')),

    # Redirect some known paths to the old site
    url(r'^images/(?P<url>.*)', 'page.views.redirect', kwargs={'prefix': "http://www.turistforeningen.no/images/"}),
    url(r'^album/(?P<url>.*)', 'page.views.redirect', kwargs={'prefix': "http://www.turistforeningen.no/album/"}),

    # Not a known view, treat it as a page
    url(r'^$', 'page.views.page', kwargs={'slug': ""}),
    url(r'^(?P<slug>.+)/$', 'page.views.page'),
)
