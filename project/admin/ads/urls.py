# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.ads.views',
    url(r'^$', 'list'),
    url(r'^ny/$', 'upload'),
)
