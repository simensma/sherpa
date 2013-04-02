from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('aktiviteter.views',
    url(r'^$', 'index'),
    url(r'^vis/(?P<aktivitet>\d+)/$', 'show'),
    url(r'^pamelding/(?P<aktivitet>\d+)/$', 'join'),
    url(r'^pamelding/bekreft/(?P<aktivitet>\d+)/$', 'join_confirm'),
)
