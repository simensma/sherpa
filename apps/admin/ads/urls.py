# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.ads.views',
    url(r'^$', 'list'),
    url(r'^ny/$', 'create_ad'),
    url(r'^oppdater/$', 'update_ad'),
    url(r'^ny-visning/$', 'create_placement'),
    url(r'^oppdater-visning/$', 'update_placement'),
)
