from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    # Sherpa3 admin interface
    url(r'^sherpa/', include('admin.urls')),

    # Articles
    url(r'^artikler/$', include('articles.urls')),

    # User authentication
    url(r'^bruker/', include('user.urls')),

    # Enrollment
    url(r'^innmelding/', include('enrollment.urls')),

    # Not a known view, treat it as a page
    url(r'^$', 'page.views.page', kwargs={'slug': ""}),
    url(r'^(?P<slug>.+)/$', 'page.views.page'),
)
