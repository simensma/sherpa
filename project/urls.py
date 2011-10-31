from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', include('home.urls')),
    url(r'^kurs/', include('training.urls')),
    url(r'^medlem/', include('member.urls')),
    url(r'^om/', include('about.urls')),

    # Sherpa3 admin interface
    url(r'^admin/', include('admin.urls')),

    # User authentication
    url(r'^innlogging/$', 'auth.views.login'),
    url(r'^utlogging/$', 'auth.views.logout'),
    url(r'^minside/$', 'auth.views.home'),

    # Not a known view, treat it as a page
    url(r'^(?P<slug>[a-zA-Z0-9\-_]+)/$', 'page.views.page'),
)
