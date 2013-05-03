from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('instagram.views',
    url(r'^$', 'default'),
    url(r'^opptur2013/$', 'opptur2013'),
    url(r'^last/$', 'load'),
)
