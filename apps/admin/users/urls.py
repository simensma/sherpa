# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.users.views',

    url(r'^$', 'index'),
    url(r'^ny/$', 'new'),
    url(r'^rediger/(?P<user>\d+)/$', 'show'),
    url(ur'^søk/$', 'search'),

    url(ur'^sett-sherpa-admin/(?P<user>\d+)/$', 'make_sherpa_admin'),

)
