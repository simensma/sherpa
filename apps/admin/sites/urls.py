# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.sites.views',

    url(r'^$', 'index'),
    url(r'^sett-opp/$', 'create'),
    url(r'^sett-opp/videre/(?P<site>\d+)/$', 'created'),

    url(r'^(?P<site>\d+)/$', 'show'),
    url(r'^(?P<site>\d+)/sider/', include('admin.sites.pages.urls')),
    url(r'^(?P<site>\d+)/nyheter/', include('admin.sites.articles.urls')),
    url(r'^(?P<site>\d+)/annonser/', include('admin.sites.ads.urls')),
    url(r'^(?P<site>\d+)/navigasjon/', include('admin.sites.navigation.urls')),
    url(r'^(?P<site>\d+)/innstillinger/', include('admin.sites.settings.urls')),
    url(r'^(?P<site>\d+)/kampanjer/', include('admin.sites.campaigns.urls')),

)
