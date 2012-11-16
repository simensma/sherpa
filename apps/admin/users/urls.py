# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.users.views',

    url(r'^$', 'index'),
    url(r'^ny/$', 'new'),
    url(r'^rediger/(?P<user>\d+)/$', 'show'),
    url(ur'^søk/$', 'search'),

    url(ur'^gi-sherpa-tilgang/(?P<user>\d+)/$', 'give_sherpa_access'),
    url(ur'^ta-bort-sherpa-tilgang/(?P<user>\d+)/$', 'revoke_sherpa_access'),
    url(ur'^sett-sherpa-admin/(?P<user>\d+)/$', 'make_sherpa_admin'),
    url(ur'^gi-tilgang/$', 'add_association_permission'),

)
