# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.ads.views',
    url(r'^$', 'list'),
    url(r'^ny/$', 'upload'),
    url(r'^oppdater/$', 'rename_ad'),
    url(r'^ny-visning/$', 'place'),
    url(r'^oppdater-visning/$', 'replace'),
)
