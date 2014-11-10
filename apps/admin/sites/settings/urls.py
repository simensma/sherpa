# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.sites.settings.views',

    url(r'^$', 'index'),
    url(r'^lagre/$', 'save'),

    url(r'^analyse/', include('admin.sites.settings.analytics.urls')),
    url(r'^cache/', include('admin.sites.settings.cache.urls')),
    url(r'^publisering/', include('admin.sites.settings.publish.urls')),

)
