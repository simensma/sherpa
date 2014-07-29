# encoding: utf-8
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('admin.sites.settings.cache.views',
    url(r'^$', 'index'),
    url(r'^slett/$', 'delete'),
)
