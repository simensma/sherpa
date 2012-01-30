from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.analytics.views',
    # Analytics
    url(r'^$', 'visitors_list'),
    url(r'^sidevisninger/(?P<visitor>\d+)/$', 'requests_list'),
)
