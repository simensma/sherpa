# encoding: utf-8
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('admin.sites.navigation.views',

    url(r'^$', 'index'),
    url(r'^meny/lagre/$', 'save_menu'),
    url(r'^videresending/lagre/$', 'save_redirect'),

)
