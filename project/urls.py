from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    # Sherpa3 admin interface
    url(r'^sherpa/', include('admin.urls')),

    # User authentication
    url(r'^innlogging/$', 'auth.views.login'),
    url(r'^utlogging/$', 'auth.views.logout'),
    url(r'^minside/$', 'auth.views.home'),

    # Not a known view, treat it as a page
    url(r'^$', 'page.views.page', kwargs={'slugs': ""}),
    url(r'^(?P<slugs>[a-zA-Z0-9\-_/]+)/$', 'page.views.page'),
)
