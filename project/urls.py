from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    # Sherpa3 admin interface
    url(r'^admin/', include('admin.urls')),

    # User authentication
    url(r'^innlogging/$', 'auth.views.login'),
    url(r'^utlogging/$', 'auth.views.logout'),
    url(r'^minside/$', 'auth.views.home'),

    # Not a known view, treat it as a page
    url(r'^$', 'page.views.page', kwargs={'slug': ""}),
    url(r'^(?P<slug>[a-zA-Z0-9\-_/]+)/$', 'page.views.page'),
)
