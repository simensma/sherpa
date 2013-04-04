from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('aktiviteter.views',
    url(r'^$', 'index'),
    url(r'^vis/(?P<aktivitet_date>\d+)/$', 'show'),
    url(r'^pamelding/(?P<aktivitet_date>\d+)/$', 'join'),
    url(r'^pamelding/bekreft/(?P<aktivitet_date>\d+)/$', 'join_confirm'),
)
