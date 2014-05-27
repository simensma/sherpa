# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.sites.views',

    url(r'^$', 'index'),
    url(r'^sider/', include('admin.sites.pages.urls')),
    url(r'^nyheter/', include('admin.sites.articles.urls')),

)
