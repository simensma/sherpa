from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^logg-inn/$', 'user.views.login'),
    url(r'^logg-ut/$', 'user.views.logout'),
    url(r'^minside/$', 'user.views.home'),
)
