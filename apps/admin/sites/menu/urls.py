# encoding: utf-8
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('admin.sites.menu.views',

    url(r'^$', 'index'),
    url(r'^ny/$', 'new'),
    url(r'^rediger/$', 'edit'),
    url(r'^sorter/$', 'reorder'),
    url(r'^slett/$', 'delete'),

)
