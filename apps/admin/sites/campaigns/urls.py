# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.sites.campaigns.views',
    url(r'^$', 'index'),
    url(r'^rediger/$', 'edit'),
    url(r'^lagre/$', 'save'),
)
