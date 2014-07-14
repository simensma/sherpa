# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.sites.campaigns.views',
    url(r'^$', 'index'),
    url(r'^rediger/$', 'edit', {'campaign': None}),
    url(r'^rediger/(?P<campaign>\d+)/$', 'edit'),
    url(r'^lagre/$', 'save'),
)
