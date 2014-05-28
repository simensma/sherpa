# encoding: utf-8
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('admin.sites.navigation.views',

    url(r'^$', 'index'),
    url(r'^meny/ny/$', 'new_menu'),
    url(r'^meny/rediger/$', 'edit_menu'),
    url(r'^meny/sorter/$', 'reorder_menu'),
    url(r'^meny/slett/$', 'delete_menu'),

)
