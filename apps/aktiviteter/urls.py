from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('aktiviteter.views',
    url(r'^$', 'index'),
    url(r'^vis/(?P<aktivitet>\d+)/$', 'show'),
)
