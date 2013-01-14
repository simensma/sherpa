from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('aktiviteter.views',
    url(r'^$', 'index'),
    url(r'^show/(?P<aktivitet>\d+)/$', 'show'),
)
