# encoding: utf-8
from django.conf.urls import patterns, include, url

urlpatterns = patterns('admin.sites.settings.views',

    url(r'^$', 'index'),
    url(r'^lagre/$', 'save'),

    url(r'^analyse/', include('admin.sites.settings.analytics.urls')),
    url(r'^cache/', include('admin.sites.settings.cache.urls')),

)
