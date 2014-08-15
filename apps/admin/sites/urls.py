# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.sites.views',

    url(r'^$', 'index'),
    url(r'^sider/', include('admin.sites.pages.urls')),
    url(r'^nyheter/', include('admin.sites.articles.urls')),
    url(r'^annonser/', include('admin.sites.ads.urls')),
    url(r'^meny/', include('admin.sites.navigation.urls')),
    url(r'^innstillinger/', include('admin.sites.settings.urls')),
    url(r'^kampanjer/', include('admin.sites.campaigns.urls')),

)