# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.cache.views',
    url(r'^$', 'index'),
    url(r'^slett/$', 'delete'),
)
