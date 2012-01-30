from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.analytics.views',
    # Analytics
    url(r'^$', 'analytics_visitors_list'),
    url(r'^sidevisninger/(?P<visitor>\d+)/$', 'analytics_requests_list'),
)
